import websocket
import threading
import time
import json

from matrix_display import MatrixDisplay

matrix = MatrixDisplay()

SERVER_URL = "ws://192.168.1.99:5000/ws"

scroll_thread = None
stop_event = threading.Event()


def scroll_text(text, speed_ms, repeat):
    """Przewija tekst z daną szybkością i ilością powtórzeń.
    :param text: Tekst do przewinięcia
    :param speed_ms: Szybkość przewijania w milisekundach
    :param repeat: Liczba powtórzeń (lub "infinity")

    :return: Wątek przewijania
    """
    global stop_event

    def scroll_loop():
        count = 0
        while not stop_event.is_set() and (repeat == "infinity" or count < repeat):
            matrix.clear()
            matrix.show(text, scroll=True, delay=speed_ms / 1000.0)
            count += 1
        print("Przewijanie zakończone")

    stop_event.clear()
    thread = threading.Thread(target=scroll_loop)
    thread.start()
    return thread


def on_message(ws, message):
    global scroll_thread, stop_event

    print(f"Odebrano wiadomość: {message}")

    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        print("Błąd: niepoprawny JSON")
        return

    text = data.get("text", "")
    mode = data.get("mode", "static")
    repeat = data.get("repeat", 1)
    speed = data.get("speed", 100)

    if not text:
        return

    if scroll_thread and scroll_thread.is_alive():
        print("Zatrzymywanie poprzedniego przewijania...")
        stop_event.set()
        scroll_thread.join()

    matrix.clear()

    if mode == "static":
        matrix.show(text, scroll=False)
    elif mode == "scroll":
        try:
            repeat = int(repeat)
        except (ValueError, TypeError):
            if repeat == "infinity":
                repeat = "infinity"
            else:
                repeat = 1

        scroll_thread = scroll_text(text, speed, repeat)


def on_error(ws, error):
    print(f"Błąd: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Połączenie WebSocket zamknięte")

def on_open(ws):
    print("Połączono z serwerem WebSocket")

def run():
    while True:
        try:
            ws = websocket.WebSocketApp(
                SERVER_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()
