from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QApplication
from PyQt6.QtCore import Qt

class AuthController(QWidget):
    """User account page for managing user preferences and settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get app instance and auth helper
        self.app = QApplication.instance()
        from App.core.user._user_auth import UserAuth
        self.auth = UserAuth(self.app)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked widget to switch between login and dashboard pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Import helper classes
        from .login_register_helper import LoginRegisterWidget
        
        # Create login/register widget
        self.login_widget = LoginRegisterWidget(self, self.auth)
        self.stacked_widget.addWidget(self.login_widget)
        
        # Dashboard widgets will be created on demand
        self.user_dashboard = None
        self.admin_dashboard = None
        
        # Connect signals
        self.login_widget.login_successful.connect(self._on_login_success)
        self.login_widget.register_successful.connect(self._on_login_success)
        
        # Check if user is already logged in - ONLY if remember_login is enabled
        if self.auth.settings.get("remember_login", False):
            current_user = self.auth.get_current_user()
            if current_user:
                self._on_login_success(current_user)
        else:
            # If remember_login is disabled, make sure we're on the login page
            self.stacked_widget.setCurrentWidget(self.login_widget)
            
            # Make sure we're logged out
            self.auth.logout()  # Use logout to properly clear the state
        
    def _on_login_success(self, user):
        """Handle successful login/registration by showing appropriate dashboard"""
        display_name = user.get("fullname") or user.get("username")
        username = user.get("username")  # Get the actual username
        user_role = user.get("role", "user").lower()
        
        # Route to proper dashboard based on user role
        if user_role == "admin":
            self._show_admin_dashboard(username)  # Pass username instead of display_name
        else:
            self._show_user_dashboard(username)  # Pass username instead of display_name
    
    def _show_user_dashboard(self, username):
        """Show the regular user dashboard"""
        # Create user dashboard if it doesn't exist
        if not self.user_dashboard:
            from App.gui.widgets.pages.user.user.user_dashboard import UserDashboard
            self.user_dashboard = UserDashboard(self, username=username)
            self.user_dashboard.logout_requested.connect(self._on_logout)
            self.stacked_widget.addWidget(self.user_dashboard)
        else:
            # Update the username if the dashboard already exists
            self.user_dashboard.update_username(username)
        
        # Switch to user dashboard
        self.stacked_widget.setCurrentWidget(self.user_dashboard)
        
        # Register the page in the content widget
        main_window = self.window()
        if hasattr(main_window, 'content'):
            main_window.content.pages['user_dashboard'] = self.user_dashboard
    
    def _show_admin_dashboard(self, username):
        """Show the admin dashboard"""
        # Create admin dashboard if it doesn't exist
        if not self.admin_dashboard:
            from App.gui.widgets.pages.user.admin.admin_dashboard import AdminDashboard
            self.admin_dashboard = AdminDashboard(self, username=username)
            self.admin_dashboard.logout_requested.connect(self._on_logout)
            self.stacked_widget.addWidget(self.admin_dashboard)
        else:
            # Update the username if the dashboard already exists
            self.admin_dashboard.update_username(username)
        
        # Switch to admin dashboard
        self.stacked_widget.setCurrentWidget(self.admin_dashboard)
        
        # Register the page in the content widget
        main_window = self.window()
        if hasattr(main_window, 'content'):
            main_window.content.pages['admin_dashboard'] = self.admin_dashboard
    
    def _on_logout(self):
        """Handle logout request by switching back to login page"""
        # Switch to login screen
        self.stacked_widget.setCurrentWidget(self.login_widget)
        
        # Reset the login form
        self.login_widget.reset_login_form()
        
        # Remove dashboard pages from content widget
        main_window = self.window()
        if hasattr(main_window, 'content'):
            if 'user_dashboard' in main_window.content.pages:
                del main_window.content.pages['user_dashboard']
            if 'admin_dashboard' in main_window.content.pages:
                del main_window.content.pages['admin_dashboard']
