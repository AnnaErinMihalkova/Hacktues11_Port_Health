import requests
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QDateTimeEdit, QComboBox, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QDateTime

from . import config

class AppointmentsTab(QWidget):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user
        self.is_doctor = (user.get("role") == "doctor")

        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
            QTableWidget {
                background-color: #d5beda;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateTimeEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
                background-color: #d5beda;
            }
            QPushButton {
                background-color: #ab7db5;
                color: white;
                border-radius: 6px;
                padding: 8px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a06dab;
            }
            QPushButton:pressed {
                background-color: #955da2;
            }
        """)

        # Table of appointments
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([
            "Date/Time",
            "Patient" if self.is_doctor else "Doctor",
            "Reason"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellClicked.connect(self.on_row_selected)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("📅 Appointments")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        layout.addWidget(self.table)

        # Add either doctor (edit) or patient (schedule) layout
        if self.is_doctor:
            # Doctor UI: reschedule selected appointment
            edit_layout = QHBoxLayout()
            edit_layout.setSpacing(10)

            edit_layout.addWidget(QLabel("Reschedule selected:"))
            self.new_datetime_edit = QDateTimeEdit()
            self.new_datetime_edit.setCalendarPopup(True)
            self.new_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
            self.new_datetime_edit.setFixedWidth(180)
            edit_layout.addWidget(self.new_datetime_edit)

            self.update_btn = QPushButton("Update")
            edit_layout.addWidget(self.update_btn)
            layout.addLayout(edit_layout)

            self.update_btn.clicked.connect(self.update_appointment)
        else:
            # Patient UI: schedule new appointment
            form_layout = QHBoxLayout()
            form_layout.setSpacing(10)

            self.doctor_combo = QComboBox()
            self.load_doctors()

            self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
            self.datetime_edit.setCalendarPopup(True)
            self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
            self.datetime_edit.setFixedWidth(180)

            self.reason_edit = QLineEdit()
            self.reason_edit.setPlaceholderText("Reason for visit")

            self.schedule_btn = QPushButton("Schedule")

            form_layout.addWidget(QLabel("Doctor:"))
            form_layout.addWidget(self.doctor_combo)
            form_layout.addWidget(QLabel("Date & Time:"))
            form_layout.addWidget(self.datetime_edit)
            form_layout.addWidget(QLabel("Reason:"))
            form_layout.addWidget(self.reason_edit)
            form_layout.addWidget(self.schedule_btn)

            layout.addLayout(form_layout)

            self.schedule_btn.clicked.connect(self.schedule_appointment)

        self.setLayout(layout)
        self.load_appointments()

    # --- Helper Methods ---

    def load_doctors(self):
        try:
            resp = requests.get(f"{config.API_URL}/users?role=doctor", headers={
                "Authorization": f"Bearer {self.token}"
            })
            if resp.status_code == 200:
                doctors = resp.json().get("doctors", [])
            else:
                doctors = []
        except Exception:
            doctors = []

        self.doctor_combo.clear()
        for doc in doctors:
            name = doc.get("name", "Doctor")
            doc_id = doc.get("id")
            self.doctor_combo.addItem(name, userData=doc_id)
        if not doctors:
            self.doctor_combo.addItem("No doctors available", userData=None)
            self.doctor_combo.setEnabled(False)
        else:
            self.doctor_combo.setEnabled(True)

    def load_appointments(self):
        self.table.setRowCount(0)
        try:
            resp = requests.get(f"{config.API_URL}/appointments", headers={
                "Authorization": f"Bearer {self.token}"
            })
            if resp.status_code == 200:
                appointments = resp.json().get("appointments", [])
            else:
                appointments = []
        except Exception:
            appointments = []

        self.appointments_data = appointments
        for appt in appointments:
            datetime_str = appt.get("datetime")
            reason = appt.get("reason", "")
            col2 = appt.get("patient_name" if self.is_doctor else "doctor_name", "")
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(datetime_str)))
            self.table.setItem(row, 1, QTableWidgetItem(col2))
            self.table.setItem(row, 2, QTableWidgetItem(reason))

        self.table.resizeColumnsToContents()

    def schedule_appointment(self):
        if self.is_doctor:
            return

        doc_id = self.doctor_combo.currentData()
        if not doc_id:
            QMessageBox.warning(self, "Scheduling Error", "No doctor selected.")
            return

        dt = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        reason = self.reason_edit.text().strip()
        if not reason:
            QMessageBox.warning(self, "Input Error", "Please provide a reason for the appointment.")
            return

        payload = {"doctorId": doc_id, "datetime": dt, "reason": reason}
        try:
            resp = requests.post(f"{config.API_URL}/appointments", json=payload,
                                 headers={"Authorization": f"Bearer {self.token}"})
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")
            return

        if resp.status_code in (200, 201):
            QMessageBox.information(self, "Appointment Scheduled", "Your appointment has been scheduled.")
            self.load_appointments()
        else:
            try:
                error_msg = resp.json().get("message", "Failed to schedule appointment.")
            except ValueError:
                error_msg = "Failed to schedule appointment."
            QMessageBox.warning(self, "Error", error_msg)

    def update_appointment(self):
        if not self.is_doctor:
            return
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "No Selection", "Please select an appointment to update.")
            return
        if not hasattr(self, 'appointments_data') or selected >= len(self.appointments_data):
            QMessageBox.warning(self, "Error", "Unable to identify selected appointment.")
            return

        appt = self.appointments_data[selected]
        appt_id = appt.get("id")
        new_dt_str = self.new_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        try:
            resp = requests.put(f"{config.API_URL}/appointments/{appt_id}",
                                json={"datetime": new_dt_str},
                                headers={"Authorization": f"Bearer {self.token}"})
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to server: {e}")
            return

        if resp.status_code == 200:
            QMessageBox.information(self, "Appointment Updated", "Appointment has been rescheduled.")
            self.load_appointments()
        else:
            try:
                error_msg = resp.json().get("message", "Failed to update appointment.")
            except ValueError:
                error_msg = "Failed to update appointment."
            QMessageBox.warning(self, "Error", error_msg)

    def on_row_selected(self, row, col):
        if self.is_doctor and hasattr(self, 'appointments_data') and row < len(self.appointments_data):
            appt = self.appointments_data[row]
            dt_str = appt.get("datetime")
            if dt_str:
                qt_dt = QDateTime.fromString(dt_str, "yyyy-MM-dd HH:mm")
                if not qt_dt.isValid():
                    qt_dt = QDateTime.fromString(dt_str, Qt.ISODate)
                if qt_dt.isValid():
                    self.new_datetime_edit.setDateTime(qt_dt)
