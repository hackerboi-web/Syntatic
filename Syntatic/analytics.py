import os
from datetime import datetime
from flask import Blueprint, request, session, jsonify
from .auth import login_required

analytics_bp = Blueprint("analytics", __name__, template_folder="../templates")


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


@analytics_bp.route("/api/analytics/event", methods=["POST"])
@login_required
def analytics_event():
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    data = request.json or {}
    sb.table("analytics_events").insert({
        "user_id": session.get("user_id"),
        "event_name": data.get("event_name"),
        "metadata": data.get("metadata", {}),
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    return jsonify({"ok": True})
