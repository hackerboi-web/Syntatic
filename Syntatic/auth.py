import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "")


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapped


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not supabase:
            flash("Supabase not configured")
            return render_template("login.html")
        res = supabase.table("users").select("*").eq("username", username).execute()
        if res.data and check_password_hash(res.data[0]["password_hash"], password):
            session["user_id"] = res.data[0]["id"]
            session["username"] = res.data[0]["username"]
            return redirect(url_for("landing"))
        flash("Invalid credentials")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not supabase:
            flash("Supabase not configured")
            return render_template("register.html")
        hashed = generate_password_hash(password)
        try:
            res = supabase.table("users").insert({"username": username, "email": email, "password_hash": hashed}).execute()
            session["user_id"] = res.data[0]["id"]
            session["username"] = username
            return redirect(url_for("landing"))
        except Exception:
            flash("Registration failed")
    return render_template("register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("landing"))


@auth_bp.route("/discord")
def discord_login():
    if not DISCORD_CLIENT_ID or not DISCORD_REDIRECT_URI:
        return "Discord not configured", 500
    return redirect(
        "https://discord.com/api/oauth2/authorize?client_id=" + DISCORD_CLIENT_ID +
        "&redirect_uri=" + DISCORD_REDIRECT_URI +
        "&response_type=code&scope=identify%20email"
    )


@auth_bp.route("/discord/callback")
def discord_callback():
    code = request.args.get("code")
    if not code or not supabase:
        return redirect(url_for("auth.login"))
    import requests
    token_res = requests.post("https://discord.com/api/oauth2/token", data={
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    token = token_res.json().get("access_token")
    user_res = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {token}"})
    discord_user = user_res.json()
    discord_id = discord_user.get("id")
    username = discord_user.get("username", "discord_user")
    existing = supabase.table("users").select("*").eq("discord_id", discord_id).execute()
    if existing.data:
        user = existing.data[0]
    else:
        res = supabase.table("users").insert({"username": username, "discord_id": discord_id, "password_hash": None}).execute()
        user = res.data[0]
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return redirect(url_for("landing"))
""" filePath">
/workspace/app/Syntatic/auth.py