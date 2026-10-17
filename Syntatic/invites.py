import os
from flask import Blueprint, render_template, request, session, jsonify
from .auth import login_required

invites_bp = Blueprint("invites", __name__, template_folder="../templates")

def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def discord_invite_url(bot_client_id, guild_id, permissions="0"):
    return f"https://discord.com/oauth2/authorize?client_id={bot_client_id}&scope=bot&permissions={permissions}&guild_id={guild_id}&disable_select=True"


@invites_bp.route("/pages/discord-bots/invite")
@login_required
def invite_page():
    sb = get_supabase()
    invites = []
    if sb:
        res = sb.table("bot_invites").select("*").eq("created_by", session.get("user_id")).order("created_at", desc=True).execute()
        invites = res.data or []
    return render_template("pages/discord-bots/invite.html", invites=invites, username=session.get("username"))


@invites_bp.route("/api/invites", methods=["POST"])
@login_required
def create_invite():
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    data = request.json or {}
    bot_slug = data.get("bot_slug")
    guild_id = data.get("guild_id")
    bot_client_id = os.environ.get(f"DISCORD_CLIENT_ID_{bot_slug.upper()}", os.environ.get("DISCORD_CLIENT_ID", ""))
    invite_url = discord_invite_url(bot_client_id, guild_id)
    row = {
        "bot_slug": bot_slug,
        "guild_id": guild_id,
        "created_by": session.get("user_id"),
        "invite_url": invite_url,
    }
    sb.table("bot_invites").insert(row).execute()
    return jsonify(row)


@invites_bp.route("/api/invites/<invite_id>", methods=["DELETE"])
@login_required
def delete_invite(invite_id):
    sb = get_supabase()
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    sb.table("bot_invites").delete().eq("id", invite_id).eq("created_by", session.get("user_id")).execute()
    return jsonify({"ok": True})
