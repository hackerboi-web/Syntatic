import os
from flask import Flask, render_template, redirect, url_for, session, request, flash
from Syntatic.auth import auth_bp, login_required
from Syntatic.pages import GROUPS, find_page
from Syntatic.chat import chat_bp, settings_for, get_supabase
from Syntatic.roblox import fetch_items, import_items

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chat_bp)
from Syntatic.Orbitix import orbitix_bp
app.register_blueprint(orbitix_bp, url_prefix="/orbitix")


@app.route("/")
def root():
    return redirect(url_for("landing"))


@app.route("/landing")
def landing():
    if not session.get("user_id"):
        return render_template("landing.html", groups=None, logged_in=False)
    return render_template("landing.html", groups=GROUPS, logged_in=True, username=session.get("username"))


@app.route("/pages/<group>")
@login_required
def group_page(group):
    group_data = GROUPS.get(group)
    if not group_data:
        return "Not found", 404
    return render_template("group.html", group=group, group_data=group_data, username=session.get("username"))


@app.route("/pages/<group>/<slug>")
@login_required
def project_page(group, slug):
    found = find_page(group, slug)
    if not found:
        return "Not found", 404
    page, group_data = found
    key = f"chat:{group}:{slug}"
    history = session.get(key, [])
    if page.get("template"):
        return render_template(page["template"], group=group, page=page, coming_soon=not page.get("implemented"), username=session.get("username"), chat_history=history, supabase_url=os.environ.get("SUPABASE_URL", ""), supabase_anon_key=os.environ.get("SUPABASE_ANON_KEY", ""))
    return render_template("page.html", group=group, page=page, coming_soon=not page.get("implemented"), username=session.get("username"), chat_history=history, supabase_url=os.environ.get("SUPABASE_URL", ""), supabase_anon_key=os.environ.get("SUPABASE_ANON_KEY", ""))


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    sb = get_supabase()
    user_id = session.get("user_id")
    if request.method == "POST":
        enabled = request.form.get("chat_saving_enabled") == "on"
        level = request.form.get("default_thinking_level", "med")
        if sb:
            existing = sb.table("user_settings").select("user_id").eq("user_id", user_id).execute()
            if existing.data:
                sb.table("user_settings").update({"chat_saving_enabled": enabled, "default_thinking_level": level}).eq("user_id", user_id).execute()
            else:
                sb.table("user_settings").insert({"user_id": user_id, "chat_saving_enabled": enabled, "default_thinking_level": level}).execute()
        flash("Settings saved")
    settings_data = settings_for(user_id)
    return render_template("settings.html", settings=settings_data, username=session.get("username"))


@app.route("/api/roblox/items")
@login_required
def roblox_items():
    return __import__("flask").jsonify(fetch_items())


@app.route("/api/roblox/import", methods=["POST"])
@login_required
def roblox_import():
    data = request.json or {}
    imported = import_items(data.get("item_ids", []))
    return __import__("flask").jsonify({"imported": imported})


if __name__ == "__main__":
    app.run(debug=False, port=3447, host="127.0.0.1")
""" filePath">
/workspace/app/Syntatic/app.py