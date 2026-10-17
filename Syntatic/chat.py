import os
import json
from flask import Blueprint, request, Response, session, g
from werkzeug.security import check_password_hash
from .pages import find_page
from .auth import login_required
from groq import Groq

chat_bp = Blueprint("chat", __name__, template_folder="../templates")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "XXXXX")
client = Groq(api_key=GROQ_API_KEY)


def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def settings_for(user_id):
    sb = get_supabase()
    if not sb or not user_id:
        return {"chat_saving_enabled": False, "default_thinking_level": "med"}
    res = sb.table("user_settings").select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    return {"chat_saving_enabled": False, "default_thinking_level": "med"}


def session_key(group, slug):
    return f"chat:{group}:{slug}"


@chat_bp.route("/pages/<group>/<slug>/chat", methods=["POST"])
@login_required
def page_chat(group, slug):
    found = find_page(group, slug)
    if not found:
        return "Not found", 404
    page, group_data = found
    data = request.json or {}
    prompt = (data.get("prompt") or "").strip()
    thinking = data.get("thinking_level") or settings_for(session.get("user_id")).get("default_thinking_level", "med")
    image_data = data.get("image")
    levels = page.get("thinking_levels", {})
    model = levels.get(thinking, page.get("model_id"))

    key = session_key(group, slug)
    history = session.get(key, [])

    if prompt.startswith("/load"):
        sb = get_supabase()
        if not sb:
            return Response("data: {\"text\": \"Supabase not configured.\"}\n\ndata: [DONE]\n\n", content_type="text/event-stream")
        sessions = sb.table("chat_sessions").select("id,created_at").eq("user_id", session["user_id"]).eq("page_key", f"{group}:{slug}").order("created_at", desc=True).execute()
        if not sessions.data:
            return Response("data: {\"text\": \"No saved chats.\"}\n\ndata: [DONE]\n\n", content_type="text/event-stream")
        target = sessions.data[0]["id"]
        if len(prompt.split()) > 1:
            target = prompt.split()[1]
        msgs = sb.table("chat_messages").select("role,content").eq("session_id", target).order("created_at").execute()
        loaded = [{"role": m["role"], "content": m["content"]} for m in (msgs.data or [])]
        session[key] = loaded
        return Response(f"data: {json.dumps({'text': 'Loaded saved conversation.'})}\n\ndata: [DONE]\n\n", content_type="text/event-stream")

    if prompt:
        history.append({"role": "user", "content": prompt})
    session[key] = history

    def generate():
        try:
            system_content = page.get("system_prompt", "") + f" You are {page.get('model_name', 'the assistant')}."
            messages = [{"role": "system", "content": system_content}] + history
            if image_data:
                messages[-1]["content"] = [
                    {"type": "text", "text": prompt if prompt else "Analyze this image."},
                    {"type": "image_url", "image_url": {"url": image_data}},
                ]
            completion = client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=512,
                stream=True,
            )
            full = ""
            for chunk in completion:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    full += delta
                    yield f"data: {json.dumps({'text': delta})}\n\n"
            history.append({"role": "assistant", "content": full})
            session[key] = history
            sb = get_supabase()
            settings = settings_for(session.get("user_id"))
            if sb and settings.get("chat_saving_enabled"):
                existing = sb.table("chat_sessions").select("id").eq("user_id", session["user_id"]).eq("page_key", f"{group}:{slug}").order("created_at", desc=True).limit(1).execute()
                if existing.data:
                    sid = existing.data[0]["id"]
                else:
                    created = sb.table("chat_sessions").insert({"user_id": session["user_id"], "page_key": f"{group}:{slug}"}).execute()
                    sid = created.data[0]["id"]
                sb.table("chat_messages").insert({"session_id": sid, "role": "user", "content": prompt}).execute()
                sb.table("chat_messages").insert({"session_id": sid, "role": "assistant", "content": full}).execute()
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'text': f'API Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

    return Response(__import__("flask").stream_with_context(generate()), content_type="text/event-stream")
