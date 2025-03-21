import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

# Dummy imports for standalone use
# Replace with your actual modules
# from . import signup_dialog
# from . import config

# Fallbacks for testing
class config:
    API_URL = "https://your.api.com"  # Replace with real API

class DummySignupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.setFixedSize(300, 200)
        self.new_email = None

    def exec_(self):
        # Simulate successful signup
        self.new_email = "newuser@example.com"
        return QDialog.Accepted

# Use real signup_dialog.SignUpDialog in production
signup_dialog = type("signup_dialog", (), {"SignUpDialog": DummySignupDialog})


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortHealth - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.token = None
        self.user = None

        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5;
                border-radius: 10px;
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #2980b9;
            }
            QPushButton {
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)

        # UI Elements
        self.title_label = QLabel("Welcome to PortHealth")
        self.title_label.setObjectName("titleLabel")
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
            response = requests.post(
                f"{config.API_URL}/auth/login",
                json={"email": email, "password": password}
            )
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server:\n{e}")
            return

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.user = data.get("user")
            self.accept()
        else:
            try:
                error_msg = response.json().get("message", "Login failed.")
            except ValueError:
                error_msg = "Login failed. Please check your credentials."
            QMessageBox.warning(self, "Login Failed", error_msg)

    def open_signup(self):
        dlg = signup_dialog.SignUpDialog()
        dlg.move(
            self.x() + (self.width() - dlg.width()) // 2,
            self.y() + (self.height() - dlg.height()) // 2
        )
        if dlg.exec_() == QDialog.Accepted:
            new_email = getattr(dlg, "new_email", None)
            if new_email:
                self.email_edit.setText(new_email)
                self.password_edit.clear()
                self.password_edit.setFocus()

    def reject(self):
        QDialog.reject(self)
        sys.exit(0)