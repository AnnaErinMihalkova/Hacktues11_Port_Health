# chat_client_thread.py
import json
import time
import websocket
from PyQt5.QtCore import QThread, pyqtSignal

class ChatClientThread(QThread):
    # Signal emitted when a new message is received.
    messageReceived = pyqtSignal(str)

    def __init__(self, token):
        super().__init__()
        self.token = token
        self.ws = None
        self.running = True

    def run(self):
        ws_url = f"ws://localhost:4000/?token={self.token}"
        # Define the WebSocketApp with callbacks.
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        # Keep the connection alive in a loop.
        while self.running:
            try:
                self.ws.run_forever()
            except Exception as e:
                print("WebSocket run_forever error:", e)
            time.sleep(1)

    def on_message(self, ws, message):
        # Emit received message to be handled in the UI.
        self.messageReceived.emit(message)

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed:", close_status_code, close_msg)

    def send_message(self, text, target_id):
        """Send a message via the WebSocket connection."""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            msg_obj = {
                "to": target_id,
                "content": text
            }
            try:
                self.ws.send(json.dumps(msg_obj))
            except Exception as e:
                print("Error sending message:", e)
        else:
            print("WebSocket is not connected. Cannot send message.")

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()
