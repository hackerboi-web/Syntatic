import json
from pathlib import Path
from flask import render_template, request, Response, stream_with_context
from .config import APP_NAME
from . import client, orbitix_bp

@orbitix_bp.route("/")
def index():
    return render_template("index.html", app_name=APP_NAME, overlay=False)

@orbitix_bp.route("/overlay")
def overlay():
    return render_template("index.html", app_name=APP_NAME, overlay=True)

@orbitix_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    model = data.get("model", "qwen/qwen3.8-27b")
    image_data = data.get("image")

    if "orpheus" in model:
        def generate_tts():
            try:
                speech_file_path = Path(__file__).resolve().parent.parent / "speech.wav"
                response = client.audio.speech.create(
                    model=model, voice="diana", response_format="wav",
                    input=prompt if prompt else "Hello from Orbitix Text to Speech.",
                )
                with open(speech_file_path, "wb") as f:
                    f.write(response.content)
                yield f"data: {json.dumps({'text': '**Success!** Audio generated and saved locally as `speech.wav`.'})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'text': f'TTS Error: {str(e)}'})}\n\n"
        return Response(stream_with_context(generate_tts()), content_type="text/event-stream")

    if "whisper" in model:
        def generate_stt():
            try:
                yield f"data: {json.dumps({'text': '**Audio To Text Model Active:** Place audio file in server dir.'})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'text': f'STT Error: {str(e)}'})}\n\n"
        return Response(stream_with_context(generate_stt()), content_type="text/event-stream")

    def generate():
        try:
            user_content = ([{"type": "text", "text": prompt if prompt else "Analyze this image."},
                             {"type": "image_url", "image_url": {"url": image_data}}] if image_data else prompt)
            completion = client.chat.completions.create(
                messages=[{"role": "system", "content": f"You are {APP_NAME}, a helpful AI."},
                          {"role": "user", "content": user_content}],
                model=model, max_tokens=512, stream=True,
            )
            for chunk in completion:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield f"data: {json.dumps({'text': delta})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'text': f'API Error: {str(e)}'})}\n\n"
    return Response(stream_with_context(generate()), content_type="text/event-stream")
