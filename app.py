import os, requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "arza123")
TOKEN = os.environ.get("TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")

START_TIME = datetime.now()

def get_uptime():
    diff = datetime.now() - START_TIME
    days = diff.days
    hrs = diff.seconds // 3600
    mins = (diff.seconds % 3600) // 60
    segs = diff.seconds % 60
    return f"{days}d {hrs}h {mins}m {segs}s"

def build_menu(sender_id=""):
    fecha = datetime.now().strftime("%A %d de %B %Y")
    hora = datetime.now().strftime("%H:%M")

    return f"""> ╭───────────────✦
> │ ✦ *E R Z A B O T - M D* ✦
> │ 🏰 *F A I R Y T A I L*
> ╰───────────────✦

> ╭───✦ *I N F O* ✦───╮
> │ 👤 @{sender_id}
> │ 📅 {fecha}
> │ ⏰ {hora}
> │ ⏳ Activo: {get_uptime()}
> │ 💠 Prefijo:.
> ╰─────────────────╯

> ╭───✦ *D E S C A R G A S* ✦───╮
> │ 🎵.play <cancion>
> │ 🎬.play2 <video>
> │ 📘.fb <link> |.facebook
> │ 📌.pinterest |.pin
> │ 📁.mediafire |.mf
> │ 📸.ig |.instagram
> │ 🎵.tiktok |.tt
> │ 🐦.x |.tw |.twitter |.tweet
> ╰─────────────────╯

> ╭───✦ *B U S Q U E D A S* ✦───╮
> │ 📌.pinsearch |.pins
> │ 📺.ytsearch |.yts
> │ 🎵.ttsearch |.tts
> ╰─────────────────╯

> ╭───✦ *I A* ✦───╮
> │ 🤖.ia |.chat |.ai
> │ 🤖.gemini |.bot
> ╰─────────────────╯

> ╭───✦ *E C O N O M I A* ✦───╮
> │ 💳.balance |.saldo
> │ 💼.work |.trabajar
> │ 🎁.daily |.diario |.claim
> │ ⛏️.minar
> │ 🏹.cazar |.hunt |.caza
> │ 🦹.rob @user
> │ 🎰.slots <cantidad>
> │ 🏦.dep depositar/retirar
> │ 🏪.tienda |.shop
> │ 🎲.apostar coin/duelo
> ╰─────────────────╯

> ╭───✦ *D I V E R S I O N* ✦───╮
> │ 🔪.kill |.asesinar
> │ 🤘.cornudo @user
> │ 🌈.gay @user
> │ 🍆.pajero @user
> │ 😎.facha @user
> │ 🧠.inteligente @user
> │ 🐀.rata @user
> │ ☠️.toxico @user
> │ 🍀.suerte
> │ 🏆.top |.topgay |.topfachas
> │.topinteligentes |.toptoxicos
> ╰─────────────────╯

> ╭───✦ *U T I L I D A D* ✦───╮
> │ 🖼️.sticker |.s
> │ 📝.toimg
> │ 🔊.tts <texto>
> │ 🌐.translate <idioma> <texto>
> │ 🌤️.clima <ciudad>
> │ 💫.tourl
> ╰─────────────────╯

> ╭───✦ *A D M I N* ✦───╮
> │ 🚫.ban @user
> │ ✅.unban @user
> │ 👢.kick @user
> │ ⬆️.promote @user
> │ ⬇️.demote @user
> │ 🔓.group open |.group close
> │ 🔗.antilink on |.antilink off
> │ 👋.welcome on |.welcome off
> ╰─────────────────╯

> ╭───✦ *C A N A L* ✦───╮
> │ 📢 Canal: https://whatsapp.com/channel/0029VbCWz5nDJ6H9P5AmWa3t
> ╰─────────────────╯

> ╭───────────────✦
> │ ⚔️ *E R Z A S C A R L E T* ⚔️
> │ 💕 By: Flext/Enzo 💕
> ╰───────────────✦"""

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    # Imagen del menú + texto
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": "https://qu.ax/TGTPM.jpg", "caption": text}
    }
    r = requests.post(url, headers=headers, json=data)
    print("Send status:", r.text)

@app.route("/")
def home():
    return "ErzaBot Live"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token invalido", 403

    data = request.get_json()
    print(data)
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            from_number = msg["from"]
            text = msg.get("text", {}).get("body", "").lower().strip()
            print(f"Mensaje de {from_number}: {text}")
            if text.startswith("."):
                # Cualquier comando que empiece con. muestra el menú
                menu = build_menu(from_number)
                send_whatsapp(from_number, menu)
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
