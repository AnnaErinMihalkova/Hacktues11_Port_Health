from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import requests
from . import appointments_tab
from .prescriptions_tab import PrescriptionsTab
from .chat_tab import ChatPage
from . import profile_tab
from . import theme
from . import main  # for logout handling
from .chat_client_thread import ChatClientThread  # Import the new chat client thread

class MainWindow(QMainWindow):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user

        self.setWindowTitle("PortHealth")
        self.resize(900, 650)
        self.setMinimumSize(800, 500)

        # Apply theme based on user preference
        if user.get("theme") == "dark":
            theme.apply_dark_theme(QApplication.instance())
        else:
            self.apply_light_theme()

        # Create main tab widget immediately
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #d5beda;
                border-radius: 10px;
                padding: 10px 20px;
                margin: 2px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #ab7db5;
                color: white;
            }
            QTabBar::tab:hover {
                background: #a06dab;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 5px;
            }
        """)

        # Create all tab pages
        self.appointments_tab = appointments_tab.AppointmentsTab(self.token, self.user)
        self.prescriptions_tab = PrescriptionsTab(self.token, self.user)
        self.chat_tab = ChatPage(self.token, self.user)
        self.profile_tab = profile_tab.ProfileTab(self.token, self.user)

        # Add tabs to the tab widget
        self.tabs.addTab(self.appointments_tab, "Appointments")
        self.tabs.addTab(self.prescriptions_tab, "Prescriptions")
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.profile_tab, "Profile")

        # Set the tab widget as the central widget
        self.setCentralWidget(self.tabs)

        # If user is a doctor, update chat contacts
        if self.user.get("role") == "doctor":
            self.update_chat_contacts()

        # Initialize and start the chat client thread
        self.init_chat_client()

    def init_chat_client(self):
        """Initialize and start the chat client thread, connecting incoming messages to the chat page."""
        self.chat_client_thread = ChatClientThread(self.token)
        self.chat_client_thread.messageReceived.connect(self.handle_incoming_message)
        self.chat_tab.set_chat_thread(self.chat_client_thread)
        self.chat_client_thread.start()

    def handle_incoming_message(self, message):
        """Handle incoming messages from the chat client thread."""
        try:
            # Directly pass the message to the chat page's append method.
            self.chat_tab.append_message(message)
        except Exception as e:
            print("Error handling incoming message:", e)

    def update_chat_contacts(self):
        """Fetch appointments and update the chat page drop-down with patient contacts."""
        try:
            response = requests.get(
                "http://localhost:4000/appointments",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                appointments = data.get("appointments", [])
                contacts = {}
                for appt in appointments:
                    # For doctors, appointments should include patient_id and patient_name.
                    if appt.get("patient_id") and appt.get("patient_name"):
                        contacts[appt["patient_id"]] = appt["patient_name"]
                self.chat_tab.update_contacts(contacts)
            else:
                print("Error fetching appointments for contacts:", response.status_code)
        except Exception as e:
            print("Exception fetching appointments for contacts:", e)

    def logout(self):
        """Log out the current user and return to the login screen."""
        main.show_login_window()
        self.close()

    def apply_light_theme(self):
        """Apply a simple light theme."""
        QApplication.instance().setStyleSheet("""
            QMainWindow {
                background-color: #f7f9fb;
            }
        """)

    def create_button(self, text):
        """Helper function to create styled buttons (if needed)."""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #d5beda;
                border: 1px solid #ab7db5;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #ab7db5;
                border-style: inset;
                color: white;
            }
        """)
        return button
