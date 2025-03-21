import requests
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
    QHBoxLayout, QVBoxLayout, QMessageBox, QApplication
)
from . import config, theme

class ProfileTab(QWidget):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user

        # Apply styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #f0f2f5;
            }
            QPushButton {
                background-color: #ab7db5;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a06dab;
            }
            QPushButton:pressed {
                background-color: #955da2;
            }
            QCheckBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QLabel {
                color: #ab7db5;
            }
        """)

        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title
        title = QLabel("👤 Profile Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- Name Field ---
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(user.get("name", ""))
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # --- Email Field ---
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_edit = QLineEdit(user.get("email", ""))
        email_layout.addWidget(self.email_edit)
        layout.addLayout(email_layout)

        # --- Role Info ---
        role = user.get("role", "")
        role_label = QLabel(f"Role: {role.capitalize()}")
        role_label.setStyleSheet("font-size: 14px; margin-top: 5px;")
        layout.addWidget(role_label)

        # --- Theme Toggle ---
        self.dark_checkbox = QCheckBox("🌙 Enable Dark Mode")
        self.dark_checkbox.setChecked(user.get("theme", "light") == "dark")
        layout.addWidget(self.dark_checkbox)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.logout_btn = QPushButton("Logout")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.logout_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # --- Signals ---
        self.save_btn.clicked.connect(self.save_profile)
        self.logout_btn.clicked.connect(self.logout)
        self.dark_checkbox.toggled.connect(self.toggle_theme)

    def toggle_theme(self, checked):
        """Apply theme immediately when checkbox toggled."""
        app = QApplication.instance()
        if checked:
            theme.apply_dark_theme(app)
        else:
            theme.apply_light_theme(app)
        # Saving happens only on Save button

    def save_profile(self):
        """Send updated profile info to backend."""
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        theme_pref = "dark" if self.dark_checkbox.isChecked() else "light"

        if not name or not email:
            QMessageBox.warning(self, "Input Error", "Name and Email cannot be empty.")
            return

        payload = {"name": name, "email": email, "theme": theme_pref}
        try:
            resp = requests.put(
                f"{config.API_URL}/auth/profile",
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"}
            )
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")
            return

        if resp.status_code == 200:
            data = resp.json().get("user", {})
            self.user.update(data)
            QMessageBox.information(self, "Profile Updated", "Your profile has been updated.")
        else:
            try:
                error_msg = resp.json().get("message", "Failed to update profile.")
            except ValueError:
                error_msg = "Failed to update profile."
            QMessageBox.warning(self, "Error", error_msg)

    def logout(self):
        """Handle user logout action."""
        main_window = self.window()
        if hasattr(main_window, 'logout'):
            main_window.logout()
