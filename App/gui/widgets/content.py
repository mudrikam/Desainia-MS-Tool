from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from .pages.settings_page import SettingsPage
from .pages.home_page import HomePage
from .header import PageHeaderWidget

class ContentWidget(QWidget):
    # Add a signal to notify when the page changes
    page_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(0)
        
        # Add header (keep at edge)
        self.header = PageHeaderWidget()
        self.layout.addWidget(self.header)
        
        # Create stacked widget with padding
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.stack)
        
        # Initialize pages
        self.pages = {}
        self._init_pages()
    
    def _init_pages(self):
        """Initialize default pages"""
        # Import pages
        from .pages.home_page import HomePage
        from .pages.settings_page import SettingsPage
        # Import the UserPage from user.py using a full absolute path to avoid ambiguity
        from .pages.user.auth_controller import AuthController
        
        # Create pages
        self.add_page('home', HomePage(self))
        self.add_page('settings', SettingsPage(self))
        
        # Add the user page and connect authentication signals
        auth_controller = AuthController(self)
        self.add_page('user', auth_controller)
        
        # Connect to login status change signal
        auth_controller.login_status_changed.connect(self._update_login_state)
        
        # Connect to login/logout events to update sidebar
        if hasattr(auth_controller.login_widget, 'login_successful'):
            auth_controller.login_widget.login_successful.connect(self._update_login_state)
        if hasattr(auth_controller.login_widget, 'register_successful'):
            auth_controller.login_widget.register_successful.connect(self._update_login_state)
        
        # Connect to logout events from both dashboards if they exist
        self._connect_logout_signals(auth_controller)
        
    def _connect_logout_signals(self, auth_controller):
        """Connect to logout signals to update UI state"""
        # This method will be called when auth_controller is loaded and
        # again when _on_login_success creates the dashboard
        
        # Connect to dashboards' logout signals if they exist
        if hasattr(auth_controller, 'user_dashboard') and auth_controller.user_dashboard:
            auth_controller.user_dashboard.logout_requested.connect(self._update_login_state)
        
        if hasattr(auth_controller, 'admin_dashboard') and auth_controller.admin_dashboard:
            auth_controller.admin_dashboard.logout_requested.connect(self._update_login_state)
            
    def _update_login_state(self, *args):
        """Update UI elements based on login state"""
        # Update the home button state in sidebar
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.update_home_button_state()

    def add_page(self, name, page_widget):
        """Add a page to the stack"""
        self.pages[name] = page_widget
        self.stack.addWidget(page_widget)
        
    def remove_page(self, name):
        """Remove a page from the stack"""
        if name in self.pages:
            self.stack.removeWidget(self.pages[name])
            del self.pages[name]
    
    def show_page(self, name):
        """Show a specific page by name"""
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])
            self.page_changed.emit(name)  # Emit signal to update sidebar highlighting
