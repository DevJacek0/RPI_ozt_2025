from flask import Flask, render_template
from flask_sock import Sock
import json


app = Flask(__name__)
sock = Sock(app)

clients = []

@app.route('/')
def index():
    return render_template('index.html')


@sock.route('/ws')
def websocket_handler(ws):
    clients.append(ws)
    try:
        while True:
            raw_message = ws.receive()

            if raw_message is None:
                break

            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            text = data.get("text")
            mode = data.get("mode", "static")
            speed = int(data.get("speed", 100)) #ms
            repeat = data.get("repeat", 1)


            for client in clients:
                if client != ws:
                    try:
                        client.send(json.dumps({
                            "status": "received",
                            "text": text,
                            "mode": mode,
                            "speed": speed,
                            "repeat": repeat
                        }))
                    except:
                        pass
    finally:
        clients.remove(ws)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
