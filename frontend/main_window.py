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
        self.resize(900, 650)
        self.setMinimumSize(800, 500)

        # Apply theme based on user preference
        if user.get("theme") == "dark":
            theme.apply_dark_theme(QApplication.instance())
        else:
            self.apply_light_theme()

        # Create main tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)

        # Apply styles to QTabWidget
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #e0e0e0;
                border-radius: 10px;
                padding: 10px 20px;
                margin: 2px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background: #2980b9;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 5px;
            }
        """)

        # Create all tab pages
        self.appointments_tab = appointments_tab.AppointmentsTab(token, user)
        self.prescriptions_tab = PrescriptionsTab(token, user)
        self.chat_tab = ChatPage(token, user)
        self.profile_tab = profile_tab.ProfileTab(token, user)

        # Add tabs to tab widget
        self.tabs.addTab(self.appointments_tab, "Appointments")
        self.tabs.addTab(self.prescriptions_tab, "Prescriptions")
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.profile_tab, "Profile")

        # Set central widget
        self.setCentralWidget(self.tabs)

    def logout(self):
        """Log out the current user and return to the login screen."""
        main.show_login_window()
        self.close()

    def apply_light_theme(self):
        """Optional light theme styling, if you want full control."""
        QApplication.instance().setStyleSheet("""
            QMainWindow {
                background-color: #f7f9fb;
            }
        """)
