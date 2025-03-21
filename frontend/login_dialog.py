import sys
import requests
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from . import signup_dialog
from . import config

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortHealth - Login")
        self.setModal(False)  # using as modeless window
        self.token = None
        self.user = None

        # UI Elements
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.signup_button = QPushButton("Sign Up")
        # Info: using a button for sign up for simplicity

        # Layouts
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("<h3>Login</h3>"), alignment=Qt.AlignCenter)
        form_layout.addWidget(self.email_edit)
        form_layout.addWidget(self.password_edit)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.login_button)
        btn_layout.addWidget(self.signup_button)
        form_layout.addLayout(btn_layout)
        self.setLayout(form_layout)

        # Signals
        self.login_button.clicked.connect(self.perform_login)
        self.signup_button.clicked.connect(self.open_signup)
    
    def perform_login(self):
        """Handle login button click: authenticate with backend."""
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
            # Successful login
            self.accept()  # close dialog with Accepted result
        else:
            # Login failed: show error message from server if available
            try:
                error_msg = response.json().get("message", "Login failed. Please check your credentials.")
            except ValueError:
                error_msg = "Login failed. Please check your credentials."
            QMessageBox.warning(self, "Login Failed", error_msg)
    
    def open_signup(self):
        """Open the sign-up dialog."""
        dlg = signup_dialog.SignUpDialog()
        # Center the signup dialog relative to login dialog
        dlg.move(self.x() + (self.width() - dlg.width())//2, self.y() + (self.height() - dlg.height())//2)
        if dlg.exec_() == QDialog.Accepted:
            # If sign-up successful, populate the email field with the new email (for convenience)
            new_email = getattr(dlg, "new_email", None)
            if new_email:
                self.email_edit.setText(new_email)
                self.password_edit.setText("")  # clear password field
                self.password_edit.setFocus()
    
    def reject(self):
        """Override reject to quit application if login dialog is cancelled."""
        QDialog.reject(self)
        sys.exit(0)
