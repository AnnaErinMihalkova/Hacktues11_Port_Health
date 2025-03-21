import json
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QFormLayout, QLineEdit, QPushButton, QMessageBox, QLabel,
    QDateEdit, QTimeEdit, QCheckBox, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush
from .config import API_URL

class PrescriptionsTab(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.prescriptions = []

        # Set up a modern gradient background and fonts
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 400, 400)
        gradient.setColorAt(0, QColor("#ffffff"))
        gradient.setColorAt(1, QColor("#f0f2f5"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setFont(QFont("Segoe UI", 13))

        # Overall stylesheet for controls
        self.setStyleSheet("""
            QLabel {
                color: #333;
            }
            QLineEdit, QDateEdit, QTimeEdit, QComboBox {
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ab7db5, stop:1 #955da2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a06dab, stop:1 #8e5ea7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #955da2, stop:1 #7a4d8a);
            }
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #ccc;
                border-radius: 8px;
            }
        """)

        # Table: 6 columns for Patient, Start Date, End Date, Medicine, Dosage, Dose Times.
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Patient", "Start Date", "End Date", "Medicine", "Dosage", "Dose Times"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # Inputs for adding a prescription (only for doctors)
        if self.user.get("role") == "doctor":
            self.patient_combo = QComboBox()
            self.patient_combo.setFixedWidth(220)
            self.patient_combo.addItem("Select Patient", None)
            self.load_patients()  # Load patients from appointments

            self.medicine_input = QLineEdit()
            self.medicine_input.setPlaceholderText("e.g., Amoxicillin")

            self.dosage_input = QLineEdit()
            self.dosage_input.setPlaceholderText("e.g., 500mg")

            # Start Date and End Date fields
            self.start_date_input = QDateEdit()
            self.start_date_input.setCalendarPopup(True)
            self.start_date_input.setDate(QDate.currentDate())

            self.end_date_input = QDateEdit()
            self.end_date_input.setCalendarPopup(True)
            self.end_date_input.setDate(QDate.currentDate().addDays(7))  # Default 1 week later

            # Dose Time inputs
            self.dose1_time = QTimeEdit()
            self.dose1_time.setTime(QTime(10, 0))  # Default 10:00 AM

            self.twice_daily_checkbox = QCheckBox("Twice Daily")
            self.twice_daily_checkbox.stateChanged.connect(self.toggle_dose2_time)

            self.dose2_time = QTimeEdit()
            self.dose2_time.setTime(QTime(18, 0))  # Default 6:00 PM
            self.dose2_time.setEnabled(False)

            self.add_button = QPushButton("Add Prescription")
            self.add_button.clicked.connect(self.add_prescription)

            # Form Layout for doctors
            self.form_layout = QFormLayout()
            self.form_layout.addRow("Patient:", self.patient_combo)
            self.form_layout.addRow("Medicine:", self.medicine_input)
            self.form_layout.addRow("Dosage:", self.dosage_input)
            self.form_layout.addRow("Start Date:", self.start_date_input)
            self.form_layout.addRow("End Date:", self.end_date_input)
            self.form_layout.addRow("Dose 1 Time:", self.dose1_time)
            self.form_layout.addRow(self.twice_daily_checkbox)
            self.form_layout.addRow("Dose 2 Time:", self.dose2_time)
            self.form_layout.addWidget(self.add_button)
        else:
            # For non-doctors, show message only.
            self.form_layout = QFormLayout()
            self.info_label = QLabel("Only doctors can add prescriptions.")
            self.info_label.setStyleSheet("color: red; font-weight: bold;")
            self.form_layout.addWidget(self.info_label)

        # Main layout
        main_layout = QVBoxLayout()
        title = QLabel("🧾 Prescriptions")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("margin-bottom: 15px;")
        main_layout.addWidget(title)
        main_layout.addWidget(self.table)
        main_layout.addSpacing(20)
        main_layout.addLayout(self.form_layout)
        # Add a spacer at the bottom for extra padding
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(main_layout)

        # Load prescriptions on start
        self.load_prescriptions()

    def toggle_dose2_time(self, state):
        """Enable or disable the second dose time based on the checkbox."""
        self.dose2_time.setEnabled(state == Qt.Checked)

    def load_patients(self):
        """Load patients from the appointments endpoint for the logged-in doctor."""
        try:
            res = requests.get(f"{API_URL}/appointments", headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code == 200:
                data = res.json()
                appointments = data.get("appointments", [])
                patients = {}
                for appt in appointments:
                    pid = appt.get("patient_id")
                    pname = appt.get("patient_name")
                    if pid and pname:
                        patients[pid] = pname
                self.patient_combo.clear()
                self.patient_combo.addItem("Select Patient", None)
                for pid, pname in patients.items():
                    self.patient_combo.addItem(pname, pid)
            else:
                self.patient_combo.clear()
                self.patient_combo.addItem("No Patients", None)
        except Exception as e:
            print("Exception loading patients:", e)
            self.patient_combo.clear()
            self.patient_combo.addItem("Error", None)

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
            # Retrieve prescription details
            patient = str(rx.get("patient_name", ""))
            start_date = str(rx.get("start_date", ""))
            end_date = str(rx.get("end_date", ""))
            med = str(rx.get("medicine", ""))
            dose = str(rx.get("dosage", ""))
            dose_times = rx.get("dose_times", [])
            dose_times_str = ", ".join(dose_times) if dose_times else ""
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(patient))
            self.table.setItem(row, 1, QTableWidgetItem(start_date))
            self.table.setItem(row, 2, QTableWidgetItem(end_date))
            self.table.setItem(row, 3, QTableWidgetItem(med))
            self.table.setItem(row, 4, QTableWidgetItem(dose))
            self.table.setItem(row, 5, QTableWidgetItem(dose_times_str))

        self.table.resizeColumnsToContents()

    def add_prescription(self):
        """Add a new prescription. Only available to doctors."""
        if self.user.get("role") != "doctor":
            QMessageBox.warning(self, "Unauthorized", "Only doctors can add prescriptions.")
            return

        # Get selected patient ID from drop-down
        patient_id = self.patient_combo.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Patient Required", "Please select a patient for this prescription.")
            return

        medicine = self.medicine_input.text().strip()
        dosage = self.dosage_input.text().strip()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        dose1 = self.dose1_time.time().toString("HH:mm")
        dose_times = [dose1]
        if self.twice_daily_checkbox.isChecked():
            dose2 = self.dose2_time.time().toString("HH:mm")
            dose_times.append(dose2)

        if not (patient_id and medicine and dosage and start_date and end_date and dose_times):
            QMessageBox.warning(self, "Input Required", "Please enter all prescription details.")
            return

        payload = {
            "patientId": patient_id,
            "medicine": medicine,
            "dosage": dosage,
            "start_date": start_date,
            "end_date": end_date,
            "dose_times": dose_times
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            res = requests.post(f"{API_URL}/prescriptions", json=payload, headers=headers)
            if res.status_code == 201:
                QMessageBox.information(self, "Success", "Prescription added.")
                self.medicine_input.clear()
                self.dosage_input.clear()
                self.start_date_input.setDate(QDate.currentDate())
                self.end_date_input.setDate(QDate.currentDate().addDays(7))
                self.dose1_time.setTime(QTime(10, 0))
                self.dose2_time.setTime(QTime(18, 0))
                self.twice_daily_checkbox.setChecked(False)
                self.load_prescriptions()
            else:
                try:
                    error_msg = res.json().get("message", "Failed to add prescription.")
                except Exception:
                    error_msg = "Failed to add prescription."
                QMessageBox.warning(self, "Server Error", error_msg)
        except Exception:
            QMessageBox.critical(self, "Network Error", "Could not connect to server.")
