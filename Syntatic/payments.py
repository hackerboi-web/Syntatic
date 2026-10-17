import os
from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify
from .auth import login_required

payments_bp = Blueprint("payments", __name__, template_folder="../templates")


def stripe_default_api_key():
    from stripe import api_key
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if key:
        api_key(key)
    return key


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


@payments_bp.route("/api/checkout", methods=["POST"])
@login_required
def create_checkout():
    data = request.json or {}
    try:
        import stripe
        key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not key:
            return jsonify({"error": "Stripe not configured"}), 500
        stripe.api_key = key
        session_obj = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": data.get("price_id"), "quantity": data.get("quantity", 1)}],
            mode="payment",
            success_url="https://syntatic.app/?success=true",
            cancel_url="https://syntatic.app/",
        )
        sb = get_supabase()
        if sb:
            sb.table("orders").insert({
                "user_id": session.get("user_id"),
                "product_id": data.get("product_id"),
                "product_type": data.get("product_type", "stripe"),
                "status": "pending",
                "stripe_session_id": session_obj.id,
                "stripe_payment_intent_id": session_obj.payment_intent,
                "amount_cents": data.get("amount_cents"),
                "currency": data.get("currency", "usd"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()
        return jsonify({"url": session_obj.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/api/stripe/webhook", methods=["POST"])
@login_required
def stripe_webhook():
    key = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    if not key:
        return "Webhook secret missing", 400
    payload = request.get_data(as_text=True)
    sig = request.headers.get("Stripe-Signature", "")
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        event = stripe.Webhook.construct_event(payload, sig, key)
    except Exception:
        return "Invalid signature", 400
    if event["type"] == "checkout.session.completed":
        session_id = event["data"]["object"].get("id")
        sb = get_supabase()
        if sb:
            sb.table("orders").update({"status": "paid", "updated_at": datetime.utcnow().isoformat()}).eq("stripe_session_id", session_id).execute()
    return "", 200


@payments_bp.route("/orders")
@login_required
def orders_page():
    sb = get_supabase()
    if not sb:
        return "Supabase not configured", 500
    res = sb.table("orders").select("*").eq("user_id", session.get("user_id")).order("created_at", desc=True).execute()
    return render_template("orders.html", orders=res.data or [], username=session.get("username"))
