import requests
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateTimeEdit, QComboBox, QVBoxLayout, QHBoxLayout, QMessageBox,
    QSpacerItem, QSizePolicy, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush
from . import config, theme
from . import main  # for logout handling

class ProfileTab(QWidget):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user

        # Apply overall styling with a subtle gradient background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f2f5, stop:1 #d5beda);
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ab7db5, stop:1 #955da2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a06dab, stop:1 #8e5ea7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #955da2, stop:1 #7a4d8a);
            }
            QLabel {
                color: #333;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("👤 Profile Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Basic Profile Section ---
        basic_layout = QVBoxLayout()

        # Name Field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setFont(QFont("Segoe UI", 14))
        self.name_edit = QLineEdit(self.user.get("name", ""))
        self.name_edit.setFont(QFont("Segoe UI", 14))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        basic_layout.addLayout(name_layout)

        # Email Field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segoe UI", 14))
        self.email_edit = QLineEdit(self.user.get("email", ""))
        self.email_edit.setFont(QFont("Segoe UI", 14))
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_edit)
        basic_layout.addLayout(email_layout)

        # Role Info
        role = self.user.get("role", "")
        role_label = QLabel(f"Role: {role.capitalize()}")
        role_label.setFont(QFont("Segoe UI", 14))
        basic_layout.addWidget(role_label)

        layout.addLayout(basic_layout)

        # Theme Toggle Button
        self.dark_toggle_btn = QPushButton("Toggle Dark Mode")
        self.dark_toggle_btn.setFont(QFont("Segoe UI", 14))
        self.dark_toggle_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.dark_toggle_btn)

        # Save and Logout Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.setFont(QFont("Segoe UI", 14))
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setFont(QFont("Segoe UI", 14))
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.logout_btn)
        layout.addLayout(btn_layout)

        # Horizontal line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #ccc; margin: 20px 0;")
        layout.addWidget(separator)

        # --- Additional Health Information (Only for Patients) ---
        if self.user.get("role") == "patient":
            health_title = QLabel("Health Information")
            health_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
            health_title.setAlignment(Qt.AlignCenter)
            layout.addWidget(health_title)

            # Age Field
            age_layout = QHBoxLayout()
            age_label = QLabel("Age:")
            age_label.setFont(QFont("Segoe UI", 14))
            self.age_edit = QLineEdit(str(self.user.get("age", "")))
            self.age_edit.setFont(QFont("Segoe UI", 14))
            age_layout.addWidget(age_label)
            age_layout.addWidget(self.age_edit)
            layout.addLayout(age_layout)

            # Weight Field
            weight_layout = QHBoxLayout()
            weight_label = QLabel("Weight (kg):")
            weight_label.setFont(QFont("Segoe UI", 14))
            self.weight_edit = QLineEdit(str(self.user.get("weight", "")))
            self.weight_edit.setFont(QFont("Segoe UI", 14))
            weight_layout.addWidget(weight_label)
            weight_layout.addWidget(self.weight_edit)
            layout.addLayout(weight_layout)

            # Allergies Field
            allergies_layout = QHBoxLayout()
            allergies_label = QLabel("Allergies:")
            allergies_label.setFont(QFont("Segoe UI", 14))
            self.allergies_edit = QLineEdit(self.user.get("allergies", ""))
            self.allergies_edit.setFont(QFont("Segoe UI", 14))
            allergies_layout.addWidget(allergies_label)
            allergies_layout.addWidget(self.allergies_edit)
            layout.addLayout(allergies_layout)

            # Chronic Diseases Field
            chronic_layout = QHBoxLayout()
            chronic_label = QLabel("Chronic Diseases:")
            chronic_label.setFont(QFont("Segoe UI", 14))
            self.chronic_edit = QLineEdit(self.user.get("chronic_diseases", ""))
            self.chronic_edit.setFont(QFont("Segoe UI", 14))
            chronic_layout.addWidget(chronic_label)
            chronic_layout.addWidget(self.chronic_edit)
            layout.addLayout(chronic_layout)

            # Save Health Info Button
            self.save_health_btn = QPushButton("Save Health Info")
            self.save_health_btn.setFont(QFont("Segoe UI", 14))
            layout.addWidget(self.save_health_btn)
            self.save_health_btn.clicked.connect(self.save_additional_info)

        # Spacer for extra bottom spacing
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

        # Connect signals
        self.save_btn.clicked.connect(self.save_profile)
        self.logout_btn.clicked.connect(self.logout)

    def toggle_theme(self):
        """Toggle between dark and light themes and update locally; saving happens on Save."""
        app = QApplication.instance()
        if "Dark" in self.dark_toggle_btn.text():
            theme.apply_dark_theme(app)
            self.dark_toggle_btn.setText("Toggle Light Mode")
        else:
            theme.apply_light_theme(app)
            self.dark_toggle_btn.setText("Toggle Dark Mode")

    def save_profile(self):
        """Send updated basic profile info to backend."""
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        # Determine theme from button text
        theme_pref = "dark" if "Light" in self.dark_toggle_btn.text() else "light"
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

    def save_additional_info(self):
        """Send additional health information to the backend (only for patients)."""
        age_text = self.age_edit.text().strip()
        weight_text = self.weight_edit.text().strip()
        allergies = self.allergies_edit.text().strip()
        chronic = self.chronic_edit.text().strip()
        try:
            age = int(age_text) if age_text else None
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid age.")
            return
        try:
            weight = float(weight_text) if weight_text else None
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid weight.")
            return
        payload = {
            "age": age,
            "weight": weight,
            "allergies": allergies,
            "chronic_diseases": chronic
        }
        try:
            resp = requests.put(
                f"{config.API_URL}/patient_info",
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if resp.status_code == 200:
                QMessageBox.information(self, "Success", "Health information updated.")
                self.user.update(payload)
            else:
                try:
                    error_msg = resp.json().get("message", "Failed to update health info.")
                except Exception:
                    error_msg = "Failed to update health info."
                QMessageBox.warning(self, "Error", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")

    def logout(self):
        """Handle user logout action."""
        main_window = self.window()
        if hasattr(main_window, 'logout'):
            main_window.logout()
