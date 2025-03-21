import requests
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
    QHBoxLayout, QVBoxLayout, QMessageBox, QApplication, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from . import config, theme
from . import main  # for logout handling

class ProfileTab(QWidget):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user

        # Apply background gradient (optional)
        palette = QPalette()
        gradient = QPixmap(600, 400)
        gradient.fill(Qt.transparent)
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Overall stylesheet for modern look
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f0f2f5, stop:1 #d5beda);
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QPushButton {
                background-color: #ab7db5;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
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
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Title label
        title = QLabel("👤 Profile Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Name Field Layout
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setFont(QFont("Segoe UI", 14))
        self.name_edit = QLineEdit(user.get("name", ""))
        self.name_edit.setFont(QFont("Segoe UI", 14))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        main_layout.addLayout(name_layout)

        # Email Field Layout
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segoe UI", 14))
        self.email_edit = QLineEdit(user.get("email", ""))
        self.email_edit.setFont(QFont("Segoe UI", 14))
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_edit)
        main_layout.addLayout(email_layout)

        # Role Information
        role = user.get("role", "")
        role_label = QLabel(f"Role: {role.capitalize()}")
        role_label.setFont(QFont("Segoe UI", 14))
        main_layout.addWidget(role_label)

        # Spacer for visual separation
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        # Theme Toggle
        self.dark_checkbox = QCheckBox("🌙 Enable Dark Mode")
        self.dark_checkbox.setFont(QFont("Segoe UI", 13))
        self.dark_checkbox.setChecked(user.get("theme", "light") == "dark")
        main_layout.addWidget(self.dark_checkbox)

        # Button Layout
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.setFont(QFont("Segoe UI", 14))
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setFont(QFont("Segoe UI", 14))
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.logout_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Signal Connections
        self.save_btn.clicked.connect(self.save_profile)
        self.logout_btn.clicked.connect(self.logout)
        self.dark_checkbox.toggled.connect(self.toggle_theme)

    def toggle_theme(self, checked):
        """Apply theme immediately when checkbox is toggled."""
        app = QApplication.instance()
        if checked:
            theme.apply_dark_theme(app)
        else:
            theme.apply_light_theme(app)
        # Save changes only when Save button is pressed

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
