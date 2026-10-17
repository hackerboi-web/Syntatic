import os
from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify
from .auth import login_required

orders_bp = Blueprint("orders", __name__, template_folder="../templates")


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


@orders_bp.route("/pages/discord-bots/request")
@login_required
def request_page():
    sb = get_supabase()
    return render_template("pages/discord-bots/request.html", username=session.get("username"), orders=[], sb=sb)


@orders_bp.route("/api/orders", methods=["POST"])
@login_required
def create_order():
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    data = request.json or {}
    existing = sb.table("custom_orders").select("*").eq("user_id", session.get("user_id")).order("created_at", desc=True).limit(10).execute()
    row = {
        "user_id": session.get("user_id"),
        "requirements": data.get("requirements", ""),
        "status": "pending",
        "stripe_session_id": data.get("stripe_session_id", ""),
        "created_at": datetime.utcnow().isoformat(),
    }
    sb.table("custom_orders").insert(row).execute()
    try:
        from .payments import stripe_default_api_key
        stripe_secret = stripe_default_api_key()
    except Exception:
        stripe_secret = ""
    if stripe_secret and data.get("stripe_session_id"):
        send_discord_notification(data.get("requirements", ""))
    return jsonify(row)


def send_discord_notification(requirements):
    webhook_url = os.environ.get("DIScord_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return
    try:
        import requests
        requests.post(webhook_url, json={"content": f"New custom bot order requested:\n{requirements[:500]}"})
    except Exception:
        pass


@orders_bp.route("/admin/orders")
@login_required
def admin_orders():
    sb = get_supabase()
    if not sb:
        return "Supabase not configured", 500
    role = session.get("role", "")
    if role != "admin":
        return "Forbidden", 403
    res = sb.table("custom_orders").select("*").order("created_at", desc=True).limit(100).execute()
    return render_template("admin/orders.html", orders=res.data or [])
