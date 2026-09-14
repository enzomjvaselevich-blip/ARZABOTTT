from flask import Flask, request
import os
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "arzabot123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")

@app.route("/")
def home():
    return "Bot funcionando"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "error", 403
    
    if request.method == "POST":
        data = request.get_json()
        # aqui va tu logica de mensajes
        print(data)
        return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
