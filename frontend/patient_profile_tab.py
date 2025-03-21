import requests
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox

from . import config

class PatientProfileTab(QWidget):
    def __init__(self, token: str, patient_id: str):
        super().__init__()
        self.token = token
        self.patient_id = patient_id
        self.init_ui()
        self.load_patient_info()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("<h3>Patient Profile</h3>"))
        self.name_label = QLabel("Name: ")
        self.email_label = QLabel("Email: ")
        self.role_label = QLabel("Role: ")
        self.theme_label = QLabel("Theme: ")
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.role_label)
        self.layout.addWidget(self.theme_label)
        self.setLayout(self.layout)

    def load_patient_info(self):
        try:
            resp = requests.get(f"{config.API_URL}/patients/{self.patient_id}",
                                headers={"Authorization": f"Bearer {self.token}"})
            if resp.status_code == 200:
                patient = resp.json().get("patient", {})
                self.name_label.setText(f"Name: {patient.get('name', '')}")
                self.email_label.setText(f"Email: {patient.get('email', '')}")
                self.role_label.setText(f"Role: {patient.get('role', '').capitalize()}")
                self.theme_label.setText(f"Theme: {patient.get('theme', '').capitalize()}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load patient information.")
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")