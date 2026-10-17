import os
from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify
from .auth import login_required

admin_bp = Blueprint("admin", __name__, template_folder="../templates")

def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def is_admin():
    return session.get("role") == "admin" or session.get("is_admin") is True


@admin_bp.route("/admin")
@login_required
def admin_dashboard():
    if not is_admin():
        return "Forbidden", 403
    sb = get_supabase()
    stats = {}
    if sb:
        users = sb.table("users").select("id", count="exact").execute()
        orders = sb.table("orders").select("id", count="exact").execute()
        stats = {"users": (users.count or 0), "orders": (orders.count or 0)}
    return render_template("admin/dashboard.html", stats=stats, username=session.get("username"))


@admin_bp.route("/admin/users")
@login_required
def admin_users():
    if not is_admin():
        return "Forbidden", 403
    sb = get_supabase()
    users = []
    if sb:
        res = sb.table("users").select("id,username,email,created_at").limit(100).execute()
        users = res.data or []
    return render_template("admin/users.html", users=users, username=session.get("username"))


@admin_bp.route("/admin/orders")
@login_required
def admin_orders():
    if not is_admin():
        return "Forbidden", 403
    sb = get_supabase()
    orders = []
    if sb:
        res = sb.table("orders").select("*").order("created_at", desc=True).limit(100).execute()
        orders = res.data or []
    return render_template("admin/orders.html", orders=orders, username=session.get("username"))


@admin_bp.route("/admin/uptime")
@login_required
def admin_uptime():
    if not is_admin():
        return "Forbidden", 403
    sb = get_supabase()
    checks = []
    if sb:
        res = sb.table("uptime_checks").select("*").order("checked_at", desc=True).limit(100).execute()
        checks = res.data or []
    return render_template("admin/uptime.html", checks=checks, username=session.get("username"))


@admin_bp.route("/admin/audit")
@login_required
def admin_audit():
    if not is_admin():
        return "Forbidden", 403
    sb = get_supabase()
    logs = []
    if sb:
        res = sb.table("audit_logs").select("*").order("created_at", desc=True).limit(100).execute()
        logs = res.data or []
    return render_template("admin/audit.html", logs=logs, username=session.get("username"))


@admin_bp.route("/api/admin/audit", methods=["POST"])
@login_required
def audit_log():
    if not is_admin():
        return jsonify({"error": "Forbidden"}), 403
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    data = request.json or {}
    sb.table("audit_logs").insert({
        "user_id": session.get("user_id"),
        "action": data.get("action"),
        "target_type": data.get("target_type"),
        "target_id": data.get("target_id"),
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    return jsonify({"ok": True})
