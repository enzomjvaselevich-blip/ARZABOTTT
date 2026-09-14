from flask import Flask, request
import requests

PHONE_NUMBER_ID = "1347863578400713"
ACCESS_TOKEN = "EAATbTwgjFQ8BSfEEKYOzZCZB9dKUO2mtg1yOKxjZBVZBYzFUvwkCfcMtPv3bsYnEGVztAZCW3YT5X3nbDpG3JAqj4WF02dtDZBUlSe7GiZAmVIgVYqcZAZCapQLsg7IQPZBY9ndEN9h5iF4oSMUKZC7Hcmz0QOlITD7KlUlcVT8fHI7wR3P2kmlxx3qiMneDSsaal05GCfFtWqUZC1ZAxHnSw0jOogGToIFJepPxDVL8T64vVKd3Sg5ppNscv0gZDZD"
VERIFY_TOKEN = "erza123"

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            msg = value["messages"][0]
            from_number = msg["from"]
            text = msg.get("text", {}).get("body", "")
            url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "type": "text",
                "text": {"body": f"Hola! Soy Erza 🤖 me dijiste: {text}"}
            }
            requests.post(url, json=payload, headers=headers)
    except:
        pass
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot Erza Online", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3085)