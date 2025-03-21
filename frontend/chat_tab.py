from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QPlainTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class ChatPage(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.chat_thread = None
        self.is_doctor = (user.get("role") == "doctor")

        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 13px;
                color: #2c3e50;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
                background-color: #fcfcfc;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
        """)

        # --- UI Elements ---

        self.chat_log = QPlainTextEdit()
        self.chat_log.setReadOnly(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")

        self.send_button = QPushButton("Send")

        # --- Top Info Layout ---
        top_layout = QHBoxLayout()
        if self.is_doctor:
            self.target_input = QLineEdit()
            self.target_input.setPlaceholderText("Patient ID")
            self.target_input.setFixedWidth(120)
            top_layout.addWidget(QLabel("To:"))
            top_layout.addWidget(self.target_input)
        else:
            doctor_name = user.get("doctor", {}).get("name")
            if doctor_name:
                top_label = QLabel(f"Chat with Dr. {doctor_name}")
                top_label.setStyleSheet("font-weight: bold; font-size: 16px;")
                top_layout.addWidget(top_label)

        top_layout.addStretch()

        # --- Message Input Layout ---
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        if not top_layout.isEmpty():
            main_layout.addLayout(top_layout)

        main_layout.addWidget(self.chat_log)
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

        # --- Signal Connections ---
        self.send_button.clicked.connect(self.send_message)
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
            target_id = self.user.get("doctor", {}).get("id") or self.user.get("doctorId")
            if not target_id:
                QMessageBox.warning(self, "Unknown Doctor", "No doctor assigned for chat.")
                return

        # Send message
        if self.chat_thread:
            self.chat_thread.send_message(text, target_id)

        self.chat_log.appendPlainText(f"You: {text}")
        self.input_field.clear()
