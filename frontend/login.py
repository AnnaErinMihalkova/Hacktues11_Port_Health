import requests
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from config import API_URL
from signup_dialog import SignupDialog

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PortHealth Login")
        self.token = None
        self.user = None
        self.setFixedSize(300, 200)

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        
        signup_button = QPushButton("Create Account")
        signup_button.clicked.connect(self.handle_signup)

        form_layout = QFormLayout()
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow(login_button)
        form_layout.addRow(signup_button)

        self.setLayout(form_layout)

    def handle_login(self):
        # ... (same as previous but with improved error handling)
    
    def handle_signup(self):
        signup_dialog = SignupDialog()
        if signup_dialog.exec_() == QDialog.Accepted:
            self.email_input.setText("")
            self.password_input.setText("")
            QMessageBox.information(self, "Success", "Account created! Please login.")