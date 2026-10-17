import os
import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, jsonify
from .auth import login_required

uptime_bp = Blueprint("uptime", __name__, template_folder="../templates")

def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def check_service(service_name):
    """Simple simulated uptime check."""
    start = time.time()
    try:
        status = "up"
        latency = int((time.time() - start) * 1000)
    except Exception:
        status = "down"
        latency = 0
    return {
        "service_name": service_name,
        "status": status,
        "latency_ms": latency,
        "checked_at": datetime.utcnow().isoformat(),
    }


@uptime_bp.route("/pages/other-websites/uptime")
@login_required
def uptime_page():
    sb = get_supabase()
    if not sb:
        return render_template("pages/other-websites/uptime.html", uptime_data=[], username=session.get("username"))
    hours = request.args.get("hours", 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    res = sb.table("uptime_checks").select("*").gte("checked_at", since.isoformat()).order("checked_at", desc=True).execute()
    uptime_data = res.data or []
    services = {"syntatic-web": 99.8, "orbitix": 100.0}
    return render_template("pages/other-websites/uptime.html", uptime_data=uptime_data, services=services, username=session.get("username"))


@uptime_bp.route("/api/uptime/check", methods=["POST"])
@login_required
def uptime_check():
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    services = request.json or {}
    results = []
    for service in services:
        result = check_service(service)
        sb.table("uptime_checks").insert(result).execute()
        results.append(result)
    return jsonify(results)


@uptime_bp.route("/api/uptime/history")
@login_required
def uptime_history():
    sb = get_supabase()
    if not sb:
        return jsonify([])
    hours = request.args.get("hours", 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    res = sb.table("uptime_checks").select("service_name,status,latency_ms,checked_at").gte("checked_at", since.isoformat()).order("checked_at", asc=True).execute()
    return jsonify(res.data or [])
