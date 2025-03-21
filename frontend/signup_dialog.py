import requests
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QRadioButton, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from . import config

class SignUpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortHealth - Sign Up")
        self.new_email = None  # to store email of newly created account
        # UI Elements
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Full Name")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setPlaceholderText("Confirm Password")
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        # Role selection
        self.patient_radio = QRadioButton("Patient")
        self.doctor_radio = QRadioButton("Doctor")
        self.patient_radio.setChecked(True)  # default to patient

        self.signup_button = QPushButton("Sign Up")
        self.cancel_button = QPushButton("Cancel")

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("<h3>Create an Account</h3>"), alignment=Qt.AlignCenter)
        main_layout.addWidget(self.name_edit)
        main_layout.addWidget(self.email_edit)
        main_layout.addWidget(self.password_edit)
        main_layout.addWidget(self.confirm_edit)
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Role:"))
        role_layout.addWidget(self.patient_radio)
        role_layout.addWidget(self.doctor_radio)
        main_layout.addLayout(role_layout)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.signup_button)
        btn_layout.addWidget(self.cancel_button)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Signals
        self.signup_button.clicked.connect(self.perform_signup)
        self.cancel_button.clicked.connect(self.reject)
    
    def perform_signup(self):
        """Handle sign-up logic and communicate with backend."""
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm = self.confirm_edit.text().strip()
        role = "patient" if self.patient_radio.isChecked() else "doctor"
        if not name or not email or not password:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        if password != confirm:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return
        try:
            response = requests.post(f"{config.API_URL}/auth/signup", json={
                "name": name,
                "email": email,
                "password": password,
                "role": role
            })
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")
            return
        if response.status_code in (200, 201):
            # Account created
            self.new_email = email
            QMessageBox.information(self, "Success", "Account created successfully! Please log in.")
            self.accept()
        else:
            # Sign-up failed (e.g., email exists)
            try:
                error_msg = response.json().get("message", "Sign-up failed.")
            except ValueError:
                error_msg = "Sign-up failed."
            QMessageBox.warning(self, "Error", error_msg)
