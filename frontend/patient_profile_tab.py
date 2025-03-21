# frontend/patient_profile_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class PatientProfileTab(QWidget):
    def __init__(self, token: str, patient_id: str):
        super().__init__()
        self.token = token
        self.patient_id = patient_id
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.info_label = QLabel(f"Displaying profile for patient ID: {self.patient_id}")
        self.layout.addWidget(self.info_label)
        self.setLayout(self.layout)
