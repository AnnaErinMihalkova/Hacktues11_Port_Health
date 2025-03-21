import json
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit, QPushButton, QMessageBox
from .config import API_URL

class PrescriptionsTab(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.prescriptions = []

        # Setup prescriptions table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date", "Medicine", "Dosage"])

        # Input fields
        self.medicine_input = QLineEdit()
        self.dosage_input = QLineEdit()
        self.add_button = QPushButton("Add Prescription")
        self.add_button.clicked.connect(self.add_prescription)

        # Form layout
        form_layout = QFormLayout()
        form_layout.addRow("Medicine:", self.medicine_input)
        form_layout.addRow("Dosage:", self.dosage_input)
        form_layout.addWidget(self.add_button)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(form_layout)
        self.setLayout(layout)

        # Load prescriptions
        self.load_prescriptions()

    def load_prescriptions(self):
        """Fetch and display prescriptions."""
        try:
            res = requests.get(f"{API_URL}/prescriptions", headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code == 200:
                self.prescriptions = res.json()
                # Ensure the response is a list
                if isinstance(self.prescriptions, str):
                    self.prescriptions = json.loads(self.prescriptions)
                if not isinstance(self.prescriptions, list):
                    self.prescriptions = []
            else:
                self.prescriptions = []
        except Exception:
            self.prescriptions = []

        self.table.setRowCount(len(self.prescriptions))
        for row, rx in enumerate(self.prescriptions):
            if not isinstance(rx, dict):  # Ensure rx is a dictionary
                continue
            self.table.setItem(row, 0, QTableWidgetItem(str(rx.get("date", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(rx.get("medicine", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(rx.get("dosage", ""))))

    def add_prescription(self):
        """Add a new prescription."""
        medicine = self.medicine_input.text().strip()
        dosage = self.dosage_input.text().strip()
        if not medicine or not dosage:
            QMessageBox.warning(self, "Error", "Please enter both medicine and dosage.")
            return
        
        payload = {"medicine": medicine, "dosage": dosage}
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            res = requests.post(f"{API_URL}/prescriptions", json=payload, headers=headers)
            if res.status_code == 201:
                QMessageBox.information(self, "Success", "Prescription added.")
                self.load_prescriptions()
            else:
                QMessageBox.warning(self, "Error", "Failed to add prescription.")
        except Exception:
            QMessageBox.critical(self, "Error", "Could not connect to server.")
