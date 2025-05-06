from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QApplication
from PyQt6.QtCore import Qt

class UserPage(QWidget):
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
        
        # Create stacked widget to switch between login and profile pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Import helper classes
        from .login_register_helper import LoginRegisterWidget
        from .user_page import UserProfilePage
        
        # Create login/register widget
        self.login_widget = LoginRegisterWidget(self, self.auth)
        self.stacked_widget.addWidget(self.login_widget)
        
        # Create user profile page but don't add it yet
        self.profile_widget = None
        
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
        """Handle successful login/registration by showing profile page"""
        display_name = user.get("fullname") or user.get("username")
        
        # Create profile page if it doesn't exist
        if not self.profile_widget:
            from .user_page import UserProfilePage
            self.profile_widget = UserProfilePage(self, username=display_name)
            self.profile_widget.logout_requested.connect(self._on_logout)
            self.stacked_widget.addWidget(self.profile_widget)
        else:
            # Update the username if the profile already exists
            self.profile_widget.update_username(display_name)
        
        # Switch to profile page
        self.stacked_widget.setCurrentWidget(self.profile_widget)
        
        # Register the page in the content widget
        main_window = self.window()
        if hasattr(main_window, 'content'):
            main_window.content.pages['user_profile'] = self.profile_widget
    
    def _on_logout(self):
        """Handle logout request by switching back to login page"""
        # Switch to login screen
        self.stacked_widget.setCurrentWidget(self.login_widget)
        
        # Reset the login form
        self.login_widget.reset_login_form()
        
        # Remove profile page from content widget
        main_window = self.window()
        if hasattr(main_window, 'content') and 'user_profile' in main_window.content.pages:
            del main_window.content.pages['user_profile']
