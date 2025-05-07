from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal

class AuthController(QWidget):
    """User account page for managing user preferences and settings."""
    # Add a signal for login status changes
    login_status_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get app instance and auth helper
        self.app = QApplication.instance()
        from App.core.user._user_auth import UserAuth
        from App.core.user._user_session_handler import session
        self.auth = UserAuth(self.app)
        self.session = session
        
        # Debug: Tampilkan status remember_login saat inisialisasi
        print(f"Initial remember_login setting: {self.auth.settings.get('remember_login', False)}")
        
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
        
        # Check if user is already logged in
        current_user = self.auth.get_current_user()
        if current_user:
            self._on_login_success(current_user)
        else:
            # If no user is logged in, make sure we're on the login page
            self.stacked_widget.setCurrentWidget(self.login_widget)
        
    def _on_login_success(self, user):
        """Handle successful login/registration by showing appropriate dashboard"""
        display_name = user.get("fullname") or user.get("username")
        username = user.get("username")  # Get the actual username
        user_role = user.get("role", "user").lower()
        
        # Set user data in session handler
        from App.core.user._user_session_handler import session
        session.set_user_data(user)
        
        # Print session data
        print("\n===== SESSION HANDLER DATA =====")
        print(f"Username: {session.get_username()}")
        print(f"User ID: {session.get_user_id()}")
        print(f"Role: {session.get_role()}")
        print(f"Full Name: {session.get_fullname()}")
        print(f"Email: {session.get_email()}")
        print(f"Is Admin: {session.is_admin()}")
        print(f"Is Logged In: {session.is_logged_in()}")
        print(f"Complete User Data: {session.get_user_data()}")
        print("================================\n")
        
        # Route to proper dashboard based on user role
        if user_role == "admin":
            self._show_admin_dashboard(username)  # Pass username instead of display_name
        else:
            self._show_user_dashboard(username)  # Pass username instead of display_name
            
        # Emit signal that login status changed
        self.login_status_changed.emit(True)
        
        # Update sidebar home button state immediately
        main_window = self.window()
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.update_home_button_state()
            
        # Tampilkan pesan login berhasil di status bar
        if hasattr(main_window, 'statusbar'):
            # Check if remember_login is enabled in auth
            remember_status = "enabled" if self.auth.settings.get("remember_login", False) else "disabled"
            main_window.statusbar.showMessage(f"Login successful for user: {username} | Remember login: {remember_status}", 5000)
    
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
        # Clear the session data
        from App.core.user._user_session_handler import session
        session.clear_session()
        
        # Print session status after logout
        print("\n===== SESSION HANDLER AFTER LOGOUT =====")
        print(f"Is Logged In: {session.is_logged_in()}")
        print(f"User Data: {session.get_user_data()}")
        print("========================================\n")
        
        # Also logout from auth
        self.auth.logout()
        
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
                
        # Emit signal that login status changed
        self.login_status_changed.emit(False)
        
        # Update sidebar home button state immediately
        if hasattr(main_window, 'sidebar'):
            main_window.sidebar.update_home_button_state()
