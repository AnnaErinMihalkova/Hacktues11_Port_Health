import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QPlainTextEdit, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Update API_BASE_URL to point to your backend on port 4000
API_BASE_URL = "http://localhost:4000"

def load_chat_history(token, room):
    try:
        resp = requests.get(
            f"{API_BASE_URL}/messages?room={room}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("messages", [])
        else:
            print("Error fetching chat history:", resp.status_code)
            return []
    except Exception as e:
        print("Exception fetching chat history:", e)
        return []

class ChatPage(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.chat_thread = None
        self.is_doctor = (user.get("role") == "doctor")
        self.currentRoom = None  # stores the current conversation room

        # Set a modern gradient background and font styles
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f0f2f5);
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QPlainTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas, monospace;
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #ab7db5;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ab7db5, stop:1 #955da2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a06dab, stop:1 #8e5ea7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #955da2, stop:1 #7a4d8a);
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QLabel {
                color: #555;
            }
        """)

        # --- Chat Log and Message Input ---
        self.chat_log = QPlainTextEdit()
        self.chat_log.setReadOnly(True)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.send_button = QPushButton("Send")
        self.load_history_button = QPushButton("Load History")

        # --- Top Section: Determine Chat Target ---
        top_layout = QHBoxLayout()
        if self.is_doctor:
            # For doctors: use a combo box to select a patient.
            self.target_combo = QComboBox()
            self.target_combo.setFixedWidth(220)
            self.target_combo.addItem("Select Patient", None)
            top_layout.addWidget(QLabel("To:"))
            top_layout.addWidget(self.target_combo)
            # When selection changes, load conversation history.
            self.target_combo.currentIndexChanged.connect(self.handle_contact_change)
        else:
            # For patients: if doctor info exists, display it; otherwise, show input with a join button.
            doctor = self.user.get("doctor")
            if doctor and doctor.get("id") and doctor.get("name"):
                top_label = QLabel(f"Chat with Dr. {doctor['name']}")
                top_label.setStyleSheet("font-weight: bold; font-size: 16px;")
                top_layout.addWidget(top_label)
            else:
                self.doctor_name_input = QLineEdit()
                self.doctor_name_input.setPlaceholderText("Enter Doctor Name")
                self.doctor_name_input.setFixedWidth(220)
                self.join_chat_button = QPushButton("Join Chat")
                self.join_chat_button.setFixedWidth(120)
                self.join_chat_button.clicked.connect(self.join_chat)
                top_layout.addWidget(QLabel("Doctor Name:"))
                top_layout.addWidget(self.doctor_name_input)
                top_layout.addWidget(self.join_chat_button)
        top_layout.addStretch()

        # --- Message Input Layout ---
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.load_history_button)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.chat_log)
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

        # --- Signal Connections ---
        self.send_button.clicked.connect(self.send_message)
        self.input_field.returnPressed.connect(self.send_message)
        self.load_history_button.clicked.connect(self.load_history)

    def set_chat_thread(self, thread):
        """Assign the background chat thread (for WebSocket messaging)."""
        self.chat_thread = thread

    def append_message(self, message):
        """Append a new message to the chat log (called from the chat thread)."""
        self.chat_log.appendPlainText(message)

    def update_contacts(self, contacts):
        """
        Update the contacts drop-down for a doctor.
        'contacts' should be a dictionary mapping patient IDs to patient names.
        """
        if self.is_doctor:
            self.target_combo.clear()
            self.target_combo.addItem("Select Patient", None)
            for patient_id, name in contacts.items():
                self.target_combo.addItem(name, patient_id)

    def handle_contact_change(self):
        """When a doctor selects a different patient, load the chat history for that room."""
        target_id = self.target_combo.currentData()
        if target_id is None:
            self.chat_log.clear()
            return
        room = f"{min(self.user['id'], target_id)}-{max(self.user['id'], target_id)}"
        self.currentRoom = room
        messages = load_chat_history(self.token, room)
        self.chat_log.clear()
        for msg in messages:
            line = f"{msg['timestamp']} - {msg['sender_name']}: {msg['content']}"
            self.chat_log.appendPlainText(line)

    def join_chat(self):
        """
        For patients without assigned doctor info:
        Use the entered doctor's name to look up the doctor, update local user info,
        compute the room, and load the chat history.
        """
        doctor_name = self.doctor_name_input.text().strip()
        if not doctor_name:
            QMessageBox.warning(self, "Missing Doctor Name", "Please enter the doctor's name.")
            return
        try:
            resp = requests.get(f"{API_BASE_URL}/doctors/search?name={doctor_name}",
                                headers={"Authorization": f"Bearer {self.token}"}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    doctor = data[0]
                    target_id = doctor["id"]
                    self.user["doctor"] = {"id": target_id, "name": doctor_name}
                    self.chat_log.appendPlainText(f"Joined chat with Dr. {doctor_name}")
                    room = f"{min(target_id, self.user['id'])}-{max(target_id, self.user['id'])}"
                    self.currentRoom = room
                    messages = load_chat_history(self.token, room)
                    self.chat_log.clear()
                    for msg in messages:
                        line = f"{msg['timestamp']} - {msg['sender_name']}: {msg['content']}"
                        self.chat_log.appendPlainText(line)
                else:
                    QMessageBox.warning(self, "Doctor Not Found", "No doctor found with that name.")
            else:
                QMessageBox.warning(self, "Error", "Error fetching doctor information.")
        except Exception as e:
            QMessageBox.warning(self, "Network Error", f"Error fetching doctor information: {e}")

    def load_history(self):
        """Load chat history for the current conversation room."""
        if self.currentRoom is None:
            QMessageBox.information(self, "No Conversation", "Please join a conversation first.")
            return
        messages = load_chat_history(self.token, self.currentRoom)
        self.chat_log.clear()
        for msg in messages:
            line = f"{msg['timestamp']} - {msg['sender_name']}: {msg['content']}"
            self.chat_log.appendPlainText(line)

    def send_message(self):
        """Send the message via the chat thread to the target user."""
        text = self.input_field.text().strip()
        if not text:
            return

        target_id = None
        if self.is_doctor:
            target_id = self.target_combo.currentData()
            if target_id is None:
                QMessageBox.warning(self, "Missing Patient", "Please select a patient to send the message.")
                return
            room = f"{min(self.user['id'], target_id)}-{max(self.user['id'], target_id)}"
        else:
            if self.user.get("doctor") and self.user["doctor"].get("id"):
                target_id = self.user["doctor"]["id"]
                room = f"{min(target_id, self.user['id'])}-{max(target_id, self.user['id'])}"
            else:
                QMessageBox.warning(self, "No Doctor", "Please join a chat with a doctor first.")
                return

        self.currentRoom = room
        if self.chat_thread:
            self.chat_thread.send_message(text, target_id)
        self.chat_log.appendPlainText(f"You: {text}")
        self.input_field.clear()
