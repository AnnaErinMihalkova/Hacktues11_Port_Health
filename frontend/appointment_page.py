import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QTableWidget, QTableWidgetItem, QDateTimeEdit, QLineEdit, QMessageBox
from PyQt5.QtCore import QDateTime, Qt
from config import API_URL

class AppointmentsPage(QWidget):
    def __init__(self, token, user):
        super().__init__()
        self.token = token
        self.user = user
        self.current_edit_id = None  # ID of appointment being edited, None if adding new
        self.appointments = []       # cache of fetched appointments

        # Setup appointments table with 3 columns
        self.table = QTableWidget(0, 3)
        if user.get("role") == "doctor":
            self.table.setHorizontalHeaderLabels(["Date/Time", "Patient", "Description"])
        else:
            self.table.setHorizontalHeaderLabels(["Date/Time", "Doctor", "Description"])
        self.table.cellClicked.connect(self.load_appointment_to_form)

        # Input fields for appointment details
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.desc_edit = QLineEdit()

        # Buttons for saving (create/update) and clearing form for new entry
        save_button = QPushButton("Save Appointment")
        new_button = QPushButton("New Appointment")
        save_button.clicked.connect(self.save_appointment)
        new_button.clicked.connect(self.new_appointment)

        # Arrange form layout
        form_layout = QFormLayout()
        form_layout.addRow("Date & Time:", self.datetime_edit)
        form_layout.addRow("Description:", self.desc_edit)
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(new_button)
        form_layout.addRow(button_layout)

        # Combine table and form in the page layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)

        # Load initial appointment data
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
            # Determine counterpart's name to show in second column
            if self.user.get("role") == "doctor":
                name = app.get("patient", {}).get("name", "")
            else:
                name = app.get("doctor", {}).get("name", "")
            desc = app.get("description", "")
            self.table.setItem(row, 0, QTableWidgetItem(dt))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(desc))

    def load_appointment_to_form(self, row, col):
        """Populate form fields with the selected appointment for editing."""
        if 0 <= row < len(self.appointments):
            app = self.appointments[row]
            self.current_edit_id = app.get("id")
            # Set the date/time field (assuming ISO format string from backend)
            dt_str = app.get("datetime") or app.get("date") or ""
            qdt = QDateTime.fromString(dt_str, Qt.ISODate)
            if qdt.isValid():
                self.datetime_edit.setDateTime(qdt)
            else:
                # If format unknown or parsing failed, just leave current
                pass
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
                # Update existing appointment
                url = f"{API_URL}/appointments/{self.current_edit_id}"
                res = requests.put(url, json=payload, headers=headers)
            else:
                # Create new appointment
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
