from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = "arza123"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Esta parte es la que Facebook necesita para validar
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Token invalido', 403
    
    if request.method == 'POST':
        data = request.json
        print(data)
        return 'OK', 200

@app.route('/')
def home():
    return 'Bot funcionando'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
