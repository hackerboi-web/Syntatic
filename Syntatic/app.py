import os
from flask import Flask, render_template, redirect, url_for, session
from Syntatic.auth import auth_bp, login_required
from Syntatic.pages import GROUPS

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.register_blueprint(auth_bp, url_prefix="/auth")
from Syntatic.Orbitix import orbitix_bp
app.register_blueprint(orbitix_bp, url_prefix="/orbitix")


def current_user():
    return session.get("username")


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
    group_data = GROUPS.get(group)
    if not group_data:
        return "Not found", 404
    page = next((p for p in group_data["pages"] if p["slug"] == slug), None)
    if not page or not page.get("implemented"):
        return render_template("page.html", group=group, page=page, coming_soon=True, username=session.get("username"))
    return render_template("page.html", group=group, page=page, coming_soon=False, username=session.get("username"))


if __name__ == "__main__":
    app.run(debug=False, port=3447, host="127.0.0.1")
""" filePath">
/workspace/app/Syntatic/app.py