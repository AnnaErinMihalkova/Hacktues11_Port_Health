import socketio
from PyQt5.QtCore import QThread, pyqtSignal


class ChatClientThread(QThread):
    new_message = pyqtSignal(str)
    reminder = pyqtSignal(str)
    connection_error = pyqtSignal(str)

    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self._is_connected = False

        # Initialize Socket.IO client
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=3, logger=False, engineio_logger=False)

        # Register event handlers
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on("chat_message", self._on_chat_message)
        self.sio.on("reminder", self._on_reminder)

    # --- Event Handlers ---
    def _on_connect(self):
        self._is_connected = True
        print("[SocketIO] Connected to server.")

    def _on_disconnect(self):
        self._is_connected = False
        print("[SocketIO] Disconnected from server.")

    def _on_chat_message(self, data):
        sender = data.get("fromName", "Partner")
        content = data.get("content", "")
        formatted = f"{sender}: {content}"
        print(f"[Message Received] {formatted}")
        self.new_message.emit(formatted)

    def _on_reminder(self, message):
        msg = message if isinstance(message, str) else str(message)
        print(f"[Reminder Received] {msg}")
        self.reminder.emit(msg)

    # --- Thread Entry Point ---
    def run(self):
        try:
            print("[SocketIO] Attempting to connect...")
            self.sio.connect(
                "http://localhost:3000",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            self.sio.wait()
        except Exception as e:
            err = f"Socket connection error: {e}"
            print(f"[Error] {err}")
            self.connection_error.emit(err)

    # --- Public Methods ---
    def send_message(self, content: str, target_id: int):
        """Send a chat message to a specific user."""
        if not self._is_connected:
            print("[Send Failed] Not connected to server.")
            return
        try:
            payload = {"to": target_id, "content": content}
            self.sio.emit("chat_message", payload)
            print(f"[Message Sent] -> {payload}")
        except Exception as e:
            print(f"[Send Error] Failed to send message: {e}")

    def disconnect(self):
        """Disconnect gracefully from the socket."""
        try:
            if self._is_connected:
                self.sio.disconnect()
                print("[SocketIO] Disconnected manually.")
        except Exception as e:
            print(f"[Disconnect Error] {e}")
