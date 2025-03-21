from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtCore import Qt

from . import appointments_tab
from .prescriptions_tab import PrescriptionsTab

from .chat_tab import ChatPage

from . import profile_tab
from . import theme
from . import main  # import main module for logout handling

class MainWindow(QMainWindow):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user
        self.setWindowTitle("PortHealth")
        self.resize(800, 600)
        # Apply theme preference
        if user.get("theme") == "dark":
            # Apply dark mode if user's preference is dark
            theme.apply_dark_theme(QApplication.instance())

        # Create tab widget and tabs
        self.tabs = QTabWidget()
        # Create tab pages
        self.appointments_tab = appointments_tab.AppointmentsTab(token, user)
        self.prescriptions_tab = PrescriptionsTab(token, user)
        self.chat_tab = ChatPage(token, user)

        self.profile_tab = profile_tab.ProfileTab(token, user)
        # Add tabs to widget
        self.tabs.addTab(self.appointments_tab, "Appointments")
        self.tabs.addTab(self.prescriptions_tab, "Prescriptions")
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.profile_tab, "Profile")
        self.setCentralWidget(self.tabs)
    
    def logout(self):
        """Log out the current user and return to the login screen."""
        # Show a new login window and close this one
        main.show_login_window()
        self.close()
