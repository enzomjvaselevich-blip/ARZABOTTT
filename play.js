import os, requests, re
from flask import Flask, request, jsonify
from datetime import datetime
import yt_dlp

app = Flask(__name__)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "arza123")
TOKEN = os.environ.get("TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
START_TIME = datetime.now()

def send_text(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

def send_image(to, image_url, caption=""):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "image", "image": {"link": image_url, "caption": caption}}
    requests.post(url, headers=headers, json=data)

def send_audio(to, audio_url, caption=""):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"link": audio_url}}
    requests.post(url, headers=headers, json=data)
    if caption:
        send_text(to, caption)

def send_video(to, video_url, caption=""):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "video", "video": {"link": video_url, "caption": caption}}
    requests.post(url, headers=headers, json=data)

# --- TU MENU ORIGINAL ---
def get_menu():
    uptime = str(datetime.now() - START_TIME).split('.')[0]
    return f"""╭───────────────✦
│ ✦ *E R Z A B O T - M D* ✦
╰───────────────✦
⏳ Activo: {uptime}
💠 Prefijo:.

*DESCARGAS*
🎵.play <cancion> - baja audio
🎬.play2 <video> - baja video
📘.fb <link>
📸.ig <link>
🎵.tiktok <link>

Escribí por ejemplo:
.play bad bunny dákiti
.tiktok https://vm.tiktok.com/...
"""

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "error", 403

    data = request.get_json()
    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            msg = value["messages"][0]
            from_num = msg["from"]
            body = msg.get("text", {}).get("body", "")
            text = body.lower().strip()
            print(f"MSG: {text}")

            if text.startswith(".menu") or text.startswith(".help"):
                send_image(from_num, "https://qu.ax/TGTPM.jpg", get_menu())

            elif text.startswith(".play "):
                query = body[5:].strip()
                send_text(from_num, f"🔎 Buscando: *{query}*...")
                # Busca en youtube y baja audio con yt-dlp
                ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True, 'default_search': 'ytsearch1'}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    audio_url = info.get('url')
                    title = info.get('title')
                    # Para Cloud API necesitamos link directo, mandamos el de youtube y explicamos
                    send_text(from_num, f"🎵 *{title}*\n\nPara descargar el audio completo necesitamos hosting de archivos. Por ahora te paso el link:\n{info.get('webpage_url')}\n\n¿Querés que lo suba como archivo de audio directo?")

            elif text.startswith(".tiktok"):
                send_text(from_num, "📥 Función TikTok en desarrollo, ya casi está. Mandame el link y lo bajo.")

            else:
                if text.startswith("."):
                    send_image(from_num, "https://qu.ax/TGTPM.jpg", get_menu())

    except Exception as e:
        print(e)
    return jsonify({"status":"ok"}), 200

@app.route("/")
def home():
    return "ErzaBot con descargas Live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
