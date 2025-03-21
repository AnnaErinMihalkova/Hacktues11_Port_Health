import sys
import requests
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from . import signup_dialog
from . import config

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortHealth - Login")
        self.setModal(False)
        self.setFixedSize(400, 300)
        self.token = None
        self.user = None

        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
                font-size: 20px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: #d5beda;
            }
            QLineEdit:focus {
                border: 1px solid #955da2;
            }
            QPushButton {
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                background-color: #ab7db5;
                color: white;
            }
            QPushButton:hover {
                background-color: #a06dab;
            }
            QPushButton:pressed {
                background-color: #955da2;
            }
        """)

        # UI Elements
        self.title_label = QLabel("Welcome to PortHealth")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.signup_button = QPushButton("Sign Up")

        # Layouts
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        form_layout.addWidget(self.title_label)
        form_layout.addWidget(self.email_edit)
        form_layout.addWidget(self.password_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addWidget(self.login_button)
        btn_layout.addWidget(self.signup_button)

        form_layout.addLayout(btn_layout)
        self.setLayout(form_layout)

        # Signals
        self.login_button.clicked.connect(self.perform_login)
        self.signup_button.clicked.connect(self.open_signup)

    def perform_login(self):
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return
        try:
            response = requests.post(f"{config.API_URL}/auth/login", json={"email": email, "password": password})
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")
            return
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.user = data.get("user")
            self.accept()
        else:
            try:
                error_msg = response.json().get("message", "Login failed. Please check your credentials.")
            except ValueError:
                error_msg = "Login failed. Please check your credentials."
            QMessageBox.warning(self, "Login Failed", error_msg)

    def open_signup(self):
        """Open the sign-up dialog."""
        from .signup_dialog import SignUpDialog  # safe import here

        dlg = SignUpDialog()
        dlg.setModal(True)
        dlg.move(
            self.x() + (self.width() - dlg.width()) // 2,
            self.y() + (self.height() - dlg.height()) // 2
        )

        if dlg.exec_() == QDialog.Accepted:
            # Signup success → prefill login email
            new_email = getattr(dlg, "new_email", None)
            if new_email:
                self.email_edit.setText(new_email)
                self.password_edit.setFocus()
