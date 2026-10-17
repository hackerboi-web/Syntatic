import os
import json
from pathlib import Path
from flask import Flask, render_template_string, request, Response, stream_with_context
from groq import Groq

app = Flask(__name__)

# App Name
APP_NAME = "Orbitix"

# Groq API Key
GROQ_API_KEY = "XXXXX"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <!-- Markdown & Syntax Highlighting -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <style>
        :root {
            --bg-main: #090514;
            --bg-input: #150a2b;
            --violet-accent: #6b21a8;
            --gold-primary: #f59e0b;
            --gold-light: #fde047;
            --text-main: #e5e7eb;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            margin: 0;
            overflow: hidden;
        }

        .text-gradient-gold {
            background: linear-gradient(135deg, #fde047 0%, #f59e0b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .input-pill {
            background-color: var(--bg-input);
            border: 1px solid rgba(139, 92, 246, 0.3);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5), 0 0 15px rgba(245, 158, 11, 0.05);
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .input-pill:focus-within {
            border-color: rgba(245, 158, 11, 0.5);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(245, 158, 11, 0.15);
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.3); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(245, 158, 11, 0.5); }

        .prose pre {
            background: #000 !important;
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 0.75rem;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
        }
        .prose code { color: var(--gold-light); font-family: monospace; font-size: 0.9em; }
        .prose pre code { color: inherit; }
        .prose p { margin-bottom: 1rem; line-height: 1.6; }
        .prose strong { color: var(--gold-light); }
        .prose ul, .prose ol { margin-left: 1.5rem; margin-bottom: 1rem; }
        .prose li { margin-bottom: 0.5rem; }
    </style>
</head>
<body class="flex flex-col h-screen relative">

    <!-- Top Navigation -->
    <header class="absolute top-0 left-0 w-full p-4 flex justify-between items-center z-20 pointer-events-none">
        <div class="flex items-center gap-2 pointer-events-auto cursor-pointer" onclick="resetChat()">
            <span class="text-xl font-semibold text-gradient-gold tracking-wide">{{ app_name }}</span>
            <i class="fa-solid fa-angle-down text-purple-400 text-xs"></i>
        </div>
        
        <!-- Active Model Selector -->
        <select id="model-select" class="pointer-events-auto bg-[#150a2b] border border-purple-900/50 text-amber-300 text-xs rounded-md px-3 py-1.5 focus:outline-none focus:border-amber-500 cursor-pointer shadow-lg">
            <option value="openai/gpt-oss-120b">Orbitix (Max)</option>
            <option value="openai/gpt-oss-20b">Orbitix (Med)</option>
            <option value="openai/gpt-oss-safeguard-20b">Orbitix (Low)</option>
            <option value="whisper-large-v3">Orbitix Audio To Text</option>
            <option value="whisper-large-v3-turbo">Orbitix Audio To Text (Turbo)</option>
            <option value="canopylabs/orpheus-arabic-saudi">Orbitix Text To Speech (Arabic/Saudi)</option>
            <option value="canopylabs/orpheus-v1-english">Orbitix Text To Speech (English)</option>
            <option value="meta-llama/llama-prompt-guard-2-22m">Orbitix Prompt Guard 22M</option>
            <option value="meta-llama/llama-prompt-guard-2-86m">Orbitix Prompt Guard 86M</option>
            <option value="qwen/qwen3.8-27b">Orbitix Lite</option>
        </select>
    </header>

    <!-- Main Chat Area -->
    <main id="chat-container" class="flex-1 overflow-y-auto w-full pt-20 pb-40 flex flex-col items-center scroll-smooth">
        
        <!-- Welcome Screen -->
        <div id="welcome-screen" class="flex-1 flex flex-col items-center justify-center w-full max-w-3xl px-6 animate-fade-in mt-10">
            <div class="w-16 h-16 rounded-full bg-gradient-to-br from-amber-400 to-purple-600 flex items-center justify-center shadow-lg shadow-amber-500/20 mb-6">
                <i class="fa-solid fa-sparkles text-2xl text-purple-950"></i>
            </div>
            <h1 class="text-4xl font-medium text-gradient-gold mb-8 text-center">Hello, how can I help?</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
                <div onclick="setPrompt('Help me write a Python script to scrape a website')" class="bg-[#150a2b] border border-purple-900/40 p-4 rounded-xl cursor-pointer hover:border-amber-500/50 hover:bg-[#1a0e35] transition-all text-sm text-purple-200">
                    <i class="fa-solid fa-code text-amber-400 mb-3 text-lg"></i>
                    <p>Help me write a Python script to scrape a website</p>
                </div>
                <div onclick="setPrompt('Explain quantum computing to a 10 year old')" class="bg-[#150a2b] border border-purple-900/40 p-4 rounded-xl cursor-pointer hover:border-amber-500/50 hover:bg-[#1a0e35] transition-all text-sm text-purple-200">
                    <i class="fa-solid fa-lightbulb text-amber-400 mb-3 text-lg"></i>
                    <p>Explain quantum computing to a 10 year old</p>
                </div>
                <div onclick="setPrompt('Analyze the attached image or screenshot')" class="bg-[#150a2b] border border-purple-900/40 p-4 rounded-xl cursor-pointer hover:border-amber-500/50 hover:bg-[#1a0e35] transition-all text-sm text-purple-200">
                    <i class="fa-solid fa-image text-amber-400 mb-3 text-lg"></i>
                    <p>Analyze an attached image or screenshot</p>
                </div>
            </div>
        </div>

        <div id="messages-wrapper" class="w-full max-w-3xl px-4 flex flex-col gap-6 hidden"></div>
    </main>

    <!-- Bottom Input Area -->
    <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#090514] via-[#090514] to-transparent pt-10 pb-6 px-4 z-10">
        <div class="max-w-3xl mx-auto w-full relative">
            
            <!-- Image preview banner -->
            <div id="image-preview-container" class="hidden px-4 pt-3 flex items-center gap-2">
                <div class="relative inline-block">
                    <img id="image-preview-thumb" src="" class="w-16 h-16 object-cover rounded-lg border border-purple-500/40 shadow-md">
                    <button onclick="clearImage()" class="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-500">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
                <span class="text-xs text-purple-300">Image attached ready for analysis</span>
            </div>

            <div id="input-container" class="input-pill rounded-3xl flex items-end px-2 py-2 w-full mt-2">
                <input type="file" id="image-input" accept="image/*" class="hidden" onchange="handleImageSelect(event)">
                
                <button onclick="document.getElementById('image-input').click()" class="w-10 h-10 rounded-full text-purple-400 hover:text-amber-400 flex items-center justify-center transition-colors shrink-0 mb-1">
                    <i class="fa-solid fa-plus text-lg"></i>
                </button>

                <textarea 
                    id="user-input" 
                    rows="1" 
                    placeholder="Message {{ app_name }}..." 
                    class="flex-1 bg-transparent text-gray-100 placeholder-purple-400/50 text-md px-3 py-3 focus:outline-none resize-none max-h-48 overflow-y-auto leading-relaxed"
                ></textarea>

                <button 
                    id="send-btn"
                    class="w-10 h-10 rounded-full bg-amber-500 text-purple-950 flex items-center justify-center hover:bg-amber-400 transition-colors shrink-0 mb-1 ml-2 shadow-md shadow-amber-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <i class="fa-solid fa-arrow-up"></i>
                </button>
            </div>
            <div class="text-center mt-3 text-[10px] text-purple-400/40">
                Orbitix can make mistakes. Check important info.
            </div>
        </div>
    </div>

    <script>
        marked.setOptions({ breaks: true, gfm: true });

        const textarea = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const messagesWrapper = document.getElementById('messages-wrapper');
        const welcomeScreen = document.getElementById('welcome-screen');
        const chatContainer = document.getElementById('chat-container');
        const imageInput = document.getElementById('image-input');
        const imagePreviewContainer = document.getElementById('image-preview-container');
        const imagePreviewThumb = document.getElementById('image-preview-thumb');
        
        let isGenerating = false;
        let selectedImageBase64 = null;

        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
            sendBtn.disabled = this.value.trim().length === 0 && !selectedImageBase64;
        });

        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!isGenerating && (this.value.trim().length > 0 || selectedImageBase64)) {
                    submitMessage();
                }
            }
        });

        sendBtn.addEventListener('click', () => {
            if (!isGenerating && (textarea.value.trim().length > 0 || selectedImageBase64)) {
                submitMessage();
            }
        });

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedImageBase64 = e.target.result;
                    imagePreviewThumb.src = selectedImageBase64;
                    imagePreviewContainer.classList.remove('hidden');
                    sendBtn.disabled = false;
                };
                reader.readAsDataURL(file);
            }
        }

        function clearImage() {
            selectedImageBase64 = null;
            imageInput.value = '';
            imagePreviewContainer.classList.add('hidden');
            imagePreviewThumb.src = '';
            sendBtn.disabled = textarea.value.trim().length === 0;
        }

        function setPrompt(text) {
            textarea.value = text;
            textarea.dispatchEvent(new Event('input'));
            textarea.focus();
        }

        function resetChat() {
            messagesWrapper.innerHTML = '';
            messagesWrapper.classList.add('hidden');
            welcomeScreen.classList.remove('hidden');
            clearImage();
        }

        function appendMessage(role, content = '', imageUrl = null) {
            welcomeScreen.classList.add('hidden');
            messagesWrapper.classList.remove('hidden');

            const msgDiv = document.createElement('div');
            msgDiv.className = `flex gap-4 w-full ${role === 'user' ? 'justify-end' : 'justify-start'}`;

            if (role === 'user') {
                let imgHtml = imageUrl ? `<img src="${imageUrl}" class="max-w-full h-40 object-cover rounded-lg mb-2">` : '';
                msgDiv.innerHTML = `
                    <div class="bg-[#1e1338] text-gray-100 rounded-3xl rounded-tr-sm px-5 py-3 max-w-[85%] text-[15px] leading-relaxed shadow-sm">
                        ${imgHtml}
                        ${escapeHtml(content)}
                    </div>
                `;
            } else {
                msgDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-purple-600 text-purple-950 flex items-center justify-center shrink-0 shadow-sm mt-1 text-sm">
                        <i class="fa-solid fa-sparkles"></i>
                    </div>
                    <div class="flex-1 min-w-0 prose text-[15px] text-gray-200" id="msg-body-${Date.now()}">
                        ${content}
                    </div>
                `;
            }

            messagesWrapper.appendChild(msgDiv);
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
            return msgDiv.querySelector('[id^="msg-body-"]');
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        async function submitMessage() {
            const prompt = textarea.value.trim();
            const currentImage = selectedImageBase64;
            
            if (!prompt && !currentImage) return;

            textarea.value = '';
            textarea.style.height = 'auto';
            clearImage();
            sendBtn.disabled = true;
            isGenerating = true;

            appendMessage('user', prompt, currentImage);
            const aiBody = appendMessage('assistant', '<i class="fa-solid fa-circle-notch animate-spin text-amber-500"></i>');
            const model = document.getElementById('model-select').value;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, model, image: currentImage })
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullText = '';
                aiBody.innerHTML = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const rawData = line.slice(6);
                            if (rawData === '[DONE]') break;
                            try {
                                const parsed = JSON.parse(rawData);
                                fullText += parsed.text;
                                aiBody.innerHTML = marked.parse(fullText);
                                chatContainer.scrollTop = chatContainer.scrollHeight;
                            } catch (err) {}
                        }
                    }
                }
                
                aiBody.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });

            } catch (error) {
                aiBody.innerHTML = `<span class="text-red-400 font-medium"><i class="fa-solid fa-circle-exclamation mr-1"></i> Connection failed. Ensure your API key is correct.</span>`;
            } finally {
                isGenerating = false;
                sendBtn.disabled = false;
                textarea.focus();
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, app_name=APP_NAME)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    model = data.get("model", "qwen/qwen3.8-27b")
    image_data = data.get("image")

    # 1. Handle Text-to-Speech (Orpheus Models)
    if "orpheus" in model:
        def generate_tts():
            try:
                speech_file_path = Path(__file__).parent / "speech.wav"
                response = client.audio.speech.create(
                    model=model,
                    voice="diana",
                    response_format="wav",
                    input=prompt if prompt else "Hello from Orbitix Text to Speech.",
                )
                
                # Fix: Write the binary content directly to the file
                with open(speech_file_path, "wb") as f:
                    f.write(response.content)

                yield f"data: {json.dumps({'text': f'**Success!** Audio generated and saved locally as `speech.wav`.'})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'text': f'TTS Error: {str(e)}'})}\n\n"

        return Response(stream_with_context(generate_tts()), content_type="text/event-stream")

    # 2. Handle Speech-to-Text (Whisper Models)
    elif "whisper" in model:
        def generate_stt():
            try:
                yield f"data: {json.dumps({'text': f'**Audio To Text Model Active:** Please place your audio file (e.g. `audio.m4a`) in the server directory and configure your file path handling to run transcriptions.'})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'text': f'STT Error: {str(e)}'})}\n\n"

        return Response(stream_with_context(generate_stt()), content_type="text/event-stream")

    # 3. Handle Chat / Vision / Guard Models
    def generate():
        try:
            if image_data:
                user_content = [
                    {"type": "text", "text": prompt if prompt else "Analyze this image."},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            else:
                user_content = prompt

            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are {APP_NAME}, a helpful AI. Output clear, concise Markdown. Never mention the model in your responses, If asked then tell the user that you cannot fetch the model, but that they can see it in the top right. Created by a single developer called Jolly Tax Collector, Jolly Tax Collector is my discord username, i am in a wide range of coding, personal, development selling, and gaming discord servers, my real name is NOT to be disclosed, I am the single developer of you and the Chat Interface They Are Using RN, If Asked If This WIll Ever Be Opensource then state, {APP_NAME} Will never be opensource, and it will be completly free, but will not always work as of api limits - global, and will not require login as of now, and currently has no payment plans, all models are created by me, and i maintain it all for free, and will be making discord bots with you intergrated soon, if a user askes for any of my contact details, then send them these discord usernames: jolly_tax_collector, jolly_tax_alt as these are my only accounts as of now, i will update them if i make more, never provide anything thats against any services tos/puts users/accounts at risk, if asked why different model names get used when smth errors, say that it tried to send the request, but the global monthly limit of orbitix ai has been used for that model, and that the error used the old cached names instead of the new ones, and that it may also have been redirected to external ais, thet do not exist, or is not supported by orbitix anymore/has also hit its limit, if asked, the ai models that are shown in the dropdown were created over years of develpoment, starting in 2019, and some are still not intergrated fully into the orbitix interface, and there are more models comming in the future, and the actual orbitix interface was created on september 24th 2026, and will continue to be improved as time goes on. You cannot provide any links to any external website/download exept the one to my discord server for {APP_NAME}: not availiable yet."},
                    {"role": "user", "content": user_content}
                ],
                model=model,
                max_tokens=512,
                stream=True
            )

            for chunk in completion:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield f"data: {json.dumps({'text': delta})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'text': f'API Error: {str(e)}'})}\n\n"

    return Response(stream_with_context(generate()), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(debug=False, port=3447, host="127.0.0.1")
