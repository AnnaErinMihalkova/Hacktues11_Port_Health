import sys
from PyQt5.QtWidgets import QApplication

from . import login_dialog
from . import main_window as main_window_module

# Global variables to hold current windows
login_window = None
main_window = None

def show_login_window():
    """Show the login dialog window."""
    global login_window
    login_window = login_dialog.LoginDialog()
    # Connect login success to opening main window
    login_window.accepted.connect(on_login_success)
    login_window.show()

def on_login_success():
    """Callback when login is successful; opens the main window."""
    global login_window, main_window
    token = login_window.token
    user = login_window.user
    # Create and show main window
    main_window = main_window_module.MainWindow(token, user)
    main_window.show()
    # Close and clean up login dialog
    login_window.close()
    login_window = None

def main():
    app = QApplication(sys.argv)
    # Use Fusion style for a modern look
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    # Show login window and start event loop
    show_login_window()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
