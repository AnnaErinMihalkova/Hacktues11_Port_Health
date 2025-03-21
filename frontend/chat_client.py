import socketio
from PyQt5.QtCore import QThread, pyqtSignal

class ChatClientThread(QThread):
    new_message = pyqtSignal(str)
    reminder = pyqtSignal(str)

    def __init__(self, token):
        super().__init__()
        self.token = token
        # Initialize Socket.IO client
        self.sio = socketio.Client()
        # Register event handlers for chat messages and reminders
        self.sio.on('chat_message', self._on_chat_message)
        self.sio.on('reminder', self._on_reminder)

    def _on_chat_message(self, data):
        # data is expected to have 'fromName' and 'content'
        sender = data.get("fromName", "Partner")
        content = data.get("content", "")
        # Emit a signal with the formatted message
        self.new_message.emit(f"{sender}: {content}")

    def _on_reminder(self, message):
        # Emit the reminder message (string) to the main thread
        self.reminder.emit(message if isinstance(message, str) else str(message))

    def run(self):
        # Connect to the Socket.IO server with JWT (passed via header)
        try:
            self.sio.connect("http://localhost:3000", headers={"Authorization": f"Bearer {self.token}"})
            # Keep the thread alive to listen for events
            self.sio.wait()
        except Exception as e:
            # If connection fails, we could emit a warning or handle reconnect
            print("Socket connection error:", e)

    def send_message(self, content, target_id):
        """Send a chat message to the given target user ID via the socket."""
        try:
            # Emit chat message event with target and content
            self.sio.emit('chat_message', {"to": target_id, "content": content})
        except Exception as e:
            print("Failed to send message:", e)

    def disconnect(self):
        """Disconnect the socket connection."""
        try:
            self.sio.disconnect()
        except Exception as e:
            print("Error disconnecting socket:", e)
