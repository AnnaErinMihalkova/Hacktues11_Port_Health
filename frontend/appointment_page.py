import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QDateTimeEdit, QLineEdit, QMessageBox, QLabel
)
from PyQt5.QtCore import QDateTime, Qt
from config import API_URL

class AppointmentsPage(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.current_edit_id = None
        self.appointments = []

        # --- StyleSheet ---
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QLineEdit, QDateTimeEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #fcfcfc;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)

        # --- Table for Appointments ---
        self.table = QTableWidget(0, 3)
        if user.get("role") == "doctor":
            self.table.setHorizontalHeaderLabels(["Date/Time", "Patient", "Description"])
        else:
            self.table.setHorizontalHeaderLabels(["Date/Time", "Doctor", "Description"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.load_appointment_to_form)

        # --- Form Inputs ---
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Description or reason...")

        save_button = QPushButton("Save Appointment")
        new_button = QPushButton("New Appointment")

        save_button.clicked.connect(self.save_appointment)
        new_button.clicked.connect(self.new_appointment)

        # --- Form Layout ---
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.addRow("📅 Date & Time:", self.datetime_edit)
        form_layout.addRow("📝 Description:", self.desc_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_button)
        btn_layout.addWidget(new_button)
        form_layout.addRow(btn_layout)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        title = QLabel("📋 Your Appointments")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")

        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.addWidget(title)
        main_layout.addWidget(self.table)
        main_layout.addSpacing(10)
        main_layout.addLayout(form_layout)

        self.setLayout(main_layout)

        self.load_appointments()

    def load_appointments(self):
        """Retrieve appointments from the server and populate the table."""
        try:
            res = requests.get(f"{API_URL}/appointments", headers={"Authorization": f"Bearer {self.token}"})
            self.appointments = res.json() if res.status_code == 200 else []
        except Exception:
            self.appointments = []

        self.table.setRowCount(len(self.appointments))
        for row, app in enumerate(self.appointments):
            dt = app.get("datetime") or app.get("date") or ""
            if self.user.get("role") == "doctor":
                name = app.get("patient", {}).get("name", "")
            else:
                name = app.get("doctor", {}).get("name", "")
            desc = app.get("description", "")
            self.table.setItem(row, 0, QTableWidgetItem(dt))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(desc))

        self.table.resizeColumnsToContents()

    def load_appointment_to_form(self, row, col):
        """Populate form fields with the selected appointment for editing."""
        if 0 <= row < len(self.appointments):
            app = self.appointments[row]
            self.current_edit_id = app.get("id")
            dt_str = app.get("datetime") or app.get("date") or ""
            qdt = QDateTime.fromString(dt_str, Qt.ISODate)
            if qdt.isValid():
                self.datetime_edit.setDateTime(qdt)
            self.desc_edit.setText(app.get("description", ""))

    def save_appointment(self):
        """Send create/update request to the server for the appointment."""
        payload = {
            "datetime": self.datetime_edit.dateTime().toString(Qt.ISODate),
            "description": self.desc_edit.text().strip()
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            if self.current_edit_id:
                url = f"{API_URL}/appointments/{self.current_edit_id}"
                res = requests.put(url, json=payload, headers=headers)
            else:
                res = requests.post(f"{API_URL}/appointments", json=payload, headers=headers)
        except Exception:
            QMessageBox.critical(self, "Error", "Failed to connect to server.")
            return

        if res.status_code in (200, 201):
            QMessageBox.information(self, "Success", "Appointment saved successfully.")
            self.load_appointments()
            self.new_appointment()
        else:
            QMessageBox.warning(self, "Error", "Could not save appointment (check data or permissions).")

    def new_appointment(self):
        """Reset the form to blank for adding a new appointment."""
        self.current_edit_id = None
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.desc_edit.clear()
