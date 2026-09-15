import os, requests, tempfile, random, json
from flask import Flask, request, jsonify
from datetime import datetime
import yt_dlp

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "arza123")
TOKEN = os.environ.get("TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
START_TIME = datetime.now()

economy = {}

def get_user(jid):
    if jid not in economy:
        economy[jid] = {"balance": 1000, "last_work": 0, "last_daily": 0}
    return economy[jid]

def wa_request(payload):
    if not TOKEN or not PHONE_ID:
        print("ERROR: Falta TOKEN o PHONE_ID")
        return None
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload)
    print(r.text)
    return r

def send_text(to, text):
    wa_request({"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text}})

def send_image(to, link, caption=""):
    wa_request({"messaging_product":"whatsapp","to":to,"type":"image","image":{"link":link,"caption":caption}})

def upload_media(file_path, mime):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/media"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, mime)}
        data = {'messaging_product': 'whatsapp'}
        r = requests.post(url, headers=headers, files=files, data=data)
        print("UPLOAD", r.text)
        return r.json().get('id') if r.status_code==200 else None

def send_media_id(to, media_id, mtype):
    wa_request({"messaging_product":"whatsapp","to":to,"type":mtype,mtype:{"id":media_id}})

def get_uptime():
    diff = datetime.now() - START_TIME
    return f"{diff.days}d {diff.seconds//3600}h {(diff.seconds%3600)//60}m {diff.seconds%60}s"

def menu_text():
    fecha = datetime.now().strftime("%A %d de %B %Y")
    hora = datetime.now().strftime("%H:%M")
    return f"""> ╭───────────────✦
> │ ✦ *E R Z A B O T - M D* ✦
> │ 🏰 *F A I R Y T A I L*
> ╰───────────────✦

> ╭───✦ *I N F O* ✦───╮
> │ 📅 {fecha}
> │ ⏰ {hora}
> │ ⏳ Activo: {get_uptime()}
> │ 💠 Prefijo:.
> ╰─────────────────╯

> ╭───✦ *D E S C A R G A S* ✦───╮
> │ 🎵.play <cancion>
> │ 🎬.play2 <video>
> │ 📘.fb <link>
> │ 📌.pin
> │ 📁.mediafire
> │ 📸.ig
> │ 🎵.tiktok
> │ 🐦.x
> ╰─────────────────╯

> ╭───✦ *B U S Q U E D A S* ✦───╮
> │ 📌.pinsearch
> │ 📺.ytsearch
> │ 🎵.ttsearch
> ╰─────────────────╯

> ╭───✦ *I A* ✦───╮
> │ 🤖.ia <texto>
> │ 🤖.gemini <texto>
> ╰─────────────────╯

> ╭───✦ *E C O N O M I A* ✦───╮
> │ 💳.balance
> │ 💼.work
> │ 🎁.daily
> │ ⛏️.minar
> │ 🏹.cazar
> │ 🦹.rob
> │ 🎰.slots <cant>
> │ 🏦.dep
> │ 🏪.tienda
> ╰─────────────────╯

> ╭───✦ *D I V E R S I O N* ✦───╮
> │ 🔪.kill @user
> │ 🤘.cornudo
> │ 🌈.gay
> │ 🍆.pajero
> │ 😎.facha
> │ 🧠.inteligente
> │ 🐀.rata
> │ ☠️.toxico
> │ 🍀.suerte
> │ 🏆.top
> ╰─────────────────╯

> ╭───✦ *U T I L I D A D* ✦───╮
> │ 🖼️.sticker (responde a imagen)
> │ 🔊.tts <texto>
> │ 🌐.translate es <texto>
> │ 🌤️.clima <ciudad>
> │ 💫.tourl (responde a imagen)
> ╰─────────────────╯

> ╭───────────────✦
> │ ⚔️ *E R Z A S C A R L E T* ⚔️
> │ 💕 By: Flext/Enzo 💕
> ╰───────────────✦"""

def download_and_send(to, query, is_video=False):
    send_text(to, f"⏳ Bajando {'video' if is_video else 'audio'}: {query}")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fmt = 'best' if is_video else 'bestaudio/best'
            opts = {'format': fmt, 'outtmpl': f'{tmp}/%(title)s.%(ext)s', 'noplaylist': True, 'quiet': True, 'default_search': 'ytsearch1' if 'http' not in query else None}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(query, download=True)
                if 'entries' in info: info = info['entries'][0]
                path = ydl.prepare_filename(info)
                mime = "video/mp4" if is_video else "audio/mpeg"
                mid = upload_media(path, mime)
                if mid:
                    send_media_id(to, mid, "video" if is_video else "audio")
                    send_text(to, f"✅ *{info.get('title')}*")
                else:
                    send_text(to, f"❌ No pude subirlo, pero acá está el link:\n{info.get('webpage_url')}")
    except Exception as e:
        send_text(to, f"❌ Error: {e}")

# --- ESTA ES LA PARTE QUE ARREGLA LA VERIFICACION ---
@app.route("/", methods=["GET"])
def home():
    # Si Meta verifica en /, tambien lo aceptamos
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token and challenge:
        if token == VERIFY_TOKEN:
            return challenge, 200
    return "ErzaBot Full Live - usa /webhook para verificar", 200

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method=="GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"VERIFICANDO: mode={mode} token={token} challenge={challenge} esperado={VERIFY_TOKEN}")
        if token == VERIFY_TOKEN:
            print("VERIFICADO OK!")
            return challenge, 200
        print("TOKEN INCORRECTO")
        return "error de verificacion", 403

    data=request.get_json()
    try:
        value=data["entry"][0]["changes"][0]["value"]
        if "messages" not in value: return jsonify({"ok":True})
        msg=value["messages"][0]
        from_num=msg["from"]
        body=msg.get("text",{}).get("body","")
        low=body.lower().strip()
        print(f"CMD: {low}")

        if low.startswith((".menu",".help",".ayuda",".comandos",".cmd",".start")):
            send_image(from_num, "https://qu.ax/TGTPM.jpg", menu_text())
        elif low.startswith(".play "):
            download_and_send(from_num, body[5:].strip(), False)
        elif low.startswith(".play2 "):
            download_and_send(from_num, body[6:].strip(), True)
        elif low.startswith((".fb ",".facebook ",".ig ",".instagram ",".tiktok ",".tt ",".x ",".tw ",".twitter ",".pin ",".pinterest ",".mf ",".mediafire ")):
            url = body.split(" ",1)[1] if " " in body else ""
            download_and_send(from_num, url, False)
        elif low.startswith((".ytsearch",".yts")):
            q=body.split(" ",1)[1] if " " in body else "erza scarlet"
            send_text(from_num, f"🔎 Buscando en YT: {q}\nhttps://www.youtube.com/results?search_query={q.replace(' ','+')}")
        elif low.startswith((".pinsearch",".pins",".ttsearch",".tts")):
            send_text(from_num, "🔎 Función de búsqueda en desarrollo, usá.play para bajar directo.")
        elif low.startswith((".ia ",".chat ",".ai ",".gemini ",".bot ")):
            prompt=body.split(" ",1)[1] if " " in body else "hola"
            try:
                r=requests.get(f"https://api.simsimi.net/v2/?text={prompt}&lc=es", timeout=10)
                ans=r.json().get('success', f"🤖 Erza IA: Recibí '{prompt}'")
                send_text(from_num, f"🤖 *ERZA IA:*\n{ans}")
            except:
                send_text(from_num, f"🤖 Erza IA: Hola! Me dijiste: {prompt}")
        elif low.startswith((".balance",".saldo")):
            u=get_user(from_num); send_text(from_num, f"💳 Balance: ${u['balance']}")
        elif low.startswith((".work",".trabajar",".minar",".cazar",".hunt")):
            u=get_user(from_num); gan=random.randint(100,500); u["balance"]+=gan; send_text(from_num, f"💼 Trabajaste y ganaste ${gan}. Total: ${u['balance']}")
        elif low.startswith((".daily",".diario",".claim")):
            u=get_user(from_num); u["balance"]+=1000; send_text(from_num, f"🎁 Daily reclamado +$1000. Total: ${u['balance']}")
        elif low.startswith(".slots"):
            try: cant=int(low.split()[1]);
            except: cant=100
            u=get_user(from_num)
            if random.random()>0.5: u["balance"]+=cant; send_text(from_num, f"🎰 Ganaste ${cant}! Balance: ${u['balance']}")
            else: u["balance"]-=cant; send_text(from_num, f"🎰 Perdiste ${cant}. Balance: ${u['balance']}")
        elif low.startswith((".dep",".tienda",".shop",".apostar",".rob")):
            send_text(from_num, "🏦 Comando de economía en modo demo - ya está conectado a tu balance.")
        elif low.startswith((".gay",".cornudo",".pajero",".facha",".inteligente",".rata",".toxico")):
            perc=random.randint(0,100); send_text(from_num, f"{low} eres {perc}% 😂")
        elif low.startswith((".kill",".asesinar")):
            send_text(from_num, "🔪 Has asesinado a @usuario 💀")
        elif low.startswith((".suerte",".top",".topgay",".topfachas")):
            send_text(from_num, "🏆 Top:\n1. Vos 100%\n2. Enzo 99%\n3. Flext 98%")
        elif low.startswith(".tts "):
            txt=body[4:];
            try:
                from gtts import gTTS
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                    gTTS(txt, lang='es').save(fp.name)
                    mid=upload_media(fp.name, "audio/mpeg")
                    if mid: send_media_id(from_num, mid, "audio")
                    os.unlink(fp.name)
            except: send_text(from_num, "🔊 Error TTS instala gtts")
        elif low.startswith(".translate"):
            parts=body.split(" ",2);
            if len(parts)>=3:
                r=requests.get(f"https://api.mymemory.translated.net/get?q={parts[2]}&langpair=es|{parts[1]}").json()
                send_text(from_num, f"🌐 Traducción: {r['responseData']['translatedText']}")
        elif low.startswith(".clima "):
            city=body[6:]; r=requests.get(f"https://wttr.in/{city}?format=3").text; send_text(from_num, f"🌤️ {r}")
        elif low.startswith((".sticker",".s",".toimg",".tourl")):
            send_text(from_num, "🖼️ En Cloud API los stickers se hacen distinto, manda una imagen y te paso el link para sticker.")
        elif low.startswith((".ban",".unban",".kick",".promote",".demote",".group",".antilink",".welcome")):
            send_text(from_num, "🚫 Los comandos de admin de grupos no funcionan en Cloud API oficial (Meta no deja). Para eso necesitás Baileys.")
        elif low.startswith("."):
            send_image(from_num, "https://qu.ax/TGTPM.jpg", menu_text())
    except Exception as e:
        print(e)
    return jsonify({"status":"ok"}),200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
