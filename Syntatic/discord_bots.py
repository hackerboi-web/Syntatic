import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from .auth import login_required
from .pages import find_page, GROUPS

discord_bots_bp = Blueprint("discord_bots", __name__, template_folder="../templates")


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def bot_supabase(bot_slug):
    """Per-bot Supabase database, falling back to the main service client."""
    url = os.environ.get(f"SUPABASE_URL_{bot_slug.upper()}", os.environ.get("SUPABASE_URL", ""))
    key = os.environ.get(f"SUPABASE_KEY_{bot_slug.upper()}", os.environ.get("SUPABASE_KEY", ""))
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


BOT_SECTIONS = ["overview", "settings", "commands", "rules", "logs", "permissions", "automation"]


@discord_bots_bp.route("/pages/discord-bots/<bot_slug>")
@discord_bots_bp.route("/pages/discord-bots/<bot_slug>/<section>")
@login_required
def bot_dashboard(bot_slug, section="overview"):
    if section not in BOT_SECTIONS:
        return "Not found", 404
    group_data = GROUPS.get("discord-bots")
    page = None
    for p in group_data["pages"]:
        if p.get("bot_slug") == bot_slug:
            page = p
            break
    if not page:
        return "Not found", 404
    return render_template(
        page["template"],
        group="discord-bots",
        page=page,
        bot_slug=bot_slug,
        section=section,
        sections=BOT_SECTIONS,
        username=session.get("username"),
    )


@discord_bots_bp.route("/api/discord/bots/<bot_slug>/guilds")
@login_required
def bot_guilds(bot_slug):
    return jsonify({"guilds": [], "bot_slug": bot_slug})


@discord_bots_bp.route("/api/discord/bots/<bot_slug>/guilds/<guild_id>/config")
@login_required
def bot_guild_config(bot_slug, guild_id):
    sb = bot_supabase(bot_slug)
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    res = sb.table("guild_configs").select("*").eq("guild_id", guild_id).execute()
    return jsonify(res.data[0] if res.data else {})


@discord_bots_bp.route("/api/discord/bots/<bot_slug>/guilds/<guild_id>/config", methods=["POST"])
@login_required
def bot_guild_config_update(bot_slug, guild_id):
    sb = bot_supabase(bot_slug)
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    data = request.json or {}
    existing = sb.table("guild_configs").select("guild_id").eq("guild_id", guild_id).execute()
    if existing.data:
        sb.table("guild_configs").update(data).eq("guild_id", guild_id).execute()
    else:
        sb.table("guild_configs").insert({"guild_id": guild_id, **data}).execute()
    return jsonify({"ok": True})


@discord_bots_bp.route("/api/discord/bots/<bot_slug>/guilds/<guild_id>/commands", methods=["POST"])
@login_required
def bot_commands(bot_slug, guild_id):
    data = request.json or {}
    return jsonify({"ok": True, "bot_slug": bot_slug, "guild_id": guild_id, "commands": data})


@discord_bots_bp.route("/api/discord/bots/<bot_slug>/guilds/<guild_id>/logs")
@login_required
def bot_logs(bot_slug, guild_id):
    sb = bot_supabase(bot_slug)
    if not sb:
        return jsonify({"error": "Supabase not configured"}), 500
    res = sb.table("command_logs").select("*").eq("guild_id", guild_id).order("created_at", desc=True).limit(50).execute()
    return jsonify(res.data or [])
