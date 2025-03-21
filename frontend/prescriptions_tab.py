import json
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QPushButton, QMessageBox, QLabel
)
from .config import API_URL

class PrescriptionsTab(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.prescriptions = []

        # Apply styling
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #fcfcfc;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
            }
        """)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["📅 Date", "💊 Medicine", "💉 Dosage"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # Inputs
        self.medicine_input = QLineEdit()
        self.medicine_input.setPlaceholderText("e.g., Amoxicillin")

        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("e.g., 500mg twice daily")

        self.add_button = QPushButton("Add Prescription")
        self.add_button.clicked.connect(self.add_prescription)

        # Form
        form_layout = QFormLayout()
        form_layout.addRow("Medicine:", self.medicine_input)
        form_layout.addRow("Dosage:", self.dosage_input)
        form_layout.addWidget(self.add_button)

        # Main layout
        layout = QVBoxLayout()
        title = QLabel("🧾 Prescriptions")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addSpacing(10)
        layout.addLayout(form_layout)

        self.setLayout(layout)

        # Load prescriptions on start
        self.load_prescriptions()

    def load_prescriptions(self):
        """Fetch and display prescriptions."""
        try:
            res = requests.get(f"{API_URL}/prescriptions", headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code == 200:
                self.prescriptions = res.json()
                if isinstance(self.prescriptions, str):
                    self.prescriptions = json.loads(self.prescriptions)
                if not isinstance(self.prescriptions, list):
                    self.prescriptions = []
            else:
                self.prescriptions = []
        except Exception:
            self.prescriptions = []

        self.table.setRowCount(0)
        for row, rx in enumerate(self.prescriptions):
            if not isinstance(rx, dict):
                continue
            date = str(rx.get("date", ""))
            med = str(rx.get("medicine", ""))
            dose = str(rx.get("dosage", ""))
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(date))
            self.table.setItem(row, 1, QTableWidgetItem(med))
            self.table.setItem(row, 2, QTableWidgetItem(dose))

        self.table.resizeColumnsToContents()

    def add_prescription(self):
        """Add a new prescription."""
        medicine = self.medicine_input.text().strip()
        dosage = self.dosage_input.text().strip()

        if not medicine or not dosage:
            QMessageBox.warning(self, "Input Required", "Please enter both medicine and dosage.")
            return

        payload = {"medicine": medicine, "dosage": dosage}
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            res = requests.post(f"{API_URL}/prescriptions", json=payload, headers=headers)
            if res.status_code == 201:
                QMessageBox.information(self, "Success", "Prescription added.")
                self.medicine_input.clear()
                self.dosage_input.clear()
                self.load_prescriptions()
            else:
                error_msg = res.json().get("message", "Failed to add prescription.")
                QMessageBox.warning(self, "Server Error", error_msg)
        except Exception:
            QMessageBox.critical(self, "Network Error", "Could not connect to server.")
