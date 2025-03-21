from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QMessageBox
from PyQt5.QtCore import Qt

class ChatPage(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.chat_thread = None  # will be set by MainWindow after thread starts
        self.is_doctor = (user.get("role") == "doctor")

        # Layout components
        self.chat_log = QPlainTextEdit()
        self.chat_log.setReadOnly(True)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        send_button = QPushButton("Send")

        # If doctor, provide a field to specify target patient ID; if patient, show whom they're chatting with
        top_layout = QHBoxLayout()
        if self.is_doctor:
            self.target_input = QLineEdit()
            self.target_input.setPlaceholderText("Patient ID")
            top_layout.addWidget(QLabel("To:"))
            top_layout.addWidget(self.target_input)
        else:
            doctor_name = user.get("doctor", {}).get("name")
            if doctor_name:
                top_layout.addWidget(QLabel(f"Chat with Dr. {doctor_name}"))
        # Main chat area layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)

        main_layout = QVBoxLayout()
        if not top_layout.isEmpty():
            main_layout.addLayout(top_layout)
        main_layout.addWidget(self.chat_log)
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

        # Connections for sending message
        send_button.clicked.connect(self.send_message)
        # Also send on Enter key in the input field
        self.input_field.returnPressed.connect(self.send_message)

    def set_chat_thread(self, thread):
        """Assign the background chat thread (for sending messages)."""
        self.chat_thread = thread

    def append_message(self, message):
        """Append a new message to the chat log (called from ChatClientThread)."""
        self.chat_log.appendPlainText(message)

    def send_message(self):
        """Send the message in the input field through the WebSocket to the target user."""
        text = self.input_field.text().strip()
        if not text:
            return
        # Determine recipient
        target_id = None
        if self.is_doctor:
            # Doctor must specify patient ID
            target_text = getattr(self, 'target_input', None).text().strip() if hasattr(self, 'target_input') else ""
            if not target_text:
                QMessageBox.warning(self, "Missing Patient", "Please enter a patient ID to send the message.")
                return
            try:
                target_id = int(target_text)
            except ValueError:
                QMessageBox.warning(self, "Invalid ID", "Please enter a valid patient ID.")
                return
        else:
            # Patient sends to their doctor (assume doctor's ID is provided in user info)
            target_id = self.user.get("doctor", {}).get("id") or self.user.get("doctorId")
            if not target_id:
                QMessageBox.warning(self, "Unknown Doctor", "No doctor assigned for chat.")
                return
        # Send the message via the chat thread
        if self.chat_thread:
            self.chat_thread.send_message(text, target_id)
        # Show the message in own log as sent by "You"
        self.chat_log.appendPlainText(f"You: {text}")
        self.input_field.clear()
