import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QMessageBox

from . import config
from .patient_profile_tab import PatientProfileTab

class DoctorActivity(QWidget):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.patient_list = QListWidget()
        self.patient_list.itemClicked.connect(self.display_patient_profile)
        self.layout.addWidget(self.patient_list)
        self.profile_stack = QStackedWidget()
        self.layout.addWidget(self.profile_stack)
        self.setLayout(self.layout)
        self.load_patients()

    def load_patients(self):
        try:
            resp = requests.get(f"{config.API_URL}/patients",
                                headers={"Authorization": f"Bearer {self.token}"})
            if resp.status_code == 200:
                patients = resp.json().get("patients", [])
                for patient in patients:
                    item = QListWidgetItem(patient.get("name", ""))
                    item.setData(1, patient.get("id", ""))
                    self.patient_list.addItem(item)
            else:
                QMessageBox.warning(self, "Error", "Failed to load patients.")
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")

    def display_patient_profile(self, item):
        patient_id = item.data(1)
        profile_tab = PatientProfileTab(self.token, patient_id)
        self.profile_stack.addWidget(profile_tab)
        self.profile_stack.setCurrentWidget(profile_tab)