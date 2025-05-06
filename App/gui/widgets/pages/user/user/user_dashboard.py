from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, 
    QApplication, QFrame, QSizePolicy, QSpacerItem, QTabWidget,
    QFileDialog, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath, QBrush
import qtawesome as qta
import datetime
import os

# Import the database module
from App.core.database import UserDashboardDB
# Import our custom sidebar widget
from App.gui.widgets.pages.user.user._user_sidebar import UserSidebar
# Import our custom widgets
from App.gui.widgets.pages.user.user._user_preferences import UserPreferencesWidget
from App.gui.widgets.pages.user.user._user_profile import UserProfileWidget


class UserDashboard(QWidget):
    """User dashboard page shown after successful login for regular users."""
    
    # Add signal for logout
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None, username="User"):
        super().__init__(parent)
        self.username = username
        
        # Get app instance 
        self.app = QApplication.instance()
        
        # Initialize database handler
        self.db_handler = UserDashboardDB(self.app)
        
        # Get user data from database
        self.user_data = self.db_handler.get_user_data(username)
        self.fullname = self.user_data.get('fullname', username) if self.user_data else username
        
        # Main layout for the entire dashboard
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Hilangkan margin konten karena sudah ada di content.py
        main_layout.setSpacing(15)  # Add spacing between panels
        
        # === LEFT PANEL (now using UserSidebar) === 
        self.sidebar = UserSidebar(self, username)
        # Connect the logout signal from sidebar to our own signal
        self.sidebar.logout_requested.connect(self.logout_requested)
        
        # === RIGHT PANEL ===
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_panel.setStyleSheet("""
            #rightPanel {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Right panel layout
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Create tab widget for right panel
        self.tab_widget = QTabWidget()
        
        # Create tabs
        dashboard_tab = QWidget()
        # Create profile tab using our new UserProfileWidget
        self.profile_widget = UserProfileWidget(self, username, self.app)
        # Use our UserPreferencesWidget for preferences tab
        self.prefs_widget = UserPreferencesWidget(self, username, self.app)
        # Connect the image_changed signal to refresh sidebar
        self.prefs_widget.image_changed.connect(self._on_profile_image_changed)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.profile_widget, "Profile")  # New Profile tab
        self.tab_widget.addTab(self.prefs_widget, "Preferences")
        
        # Set a connection for tab changes
        self.tab_widget.currentChanged.connect(self._handle_tab_changed)
        
        # Add tab widget to right layout
        right_layout.addWidget(self.tab_widget)
        
        # Add panels to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(right_panel, 1)  # Right panel takes remaining space
    
    def _handle_tab_changed(self, index):
        """Handle tab change events"""
        # If changing to profile tab (index 1), refresh profile data
        if index == 1:  # Profile tab
            self.profile_widget.refresh_data()
        # If changing to preferences tab (index 2), refresh user data
        elif index == 2:  # Preferences tab
            self.prefs_widget.refresh_data()
    
    def _on_profile_image_changed(self):
        """Handler when profile image changes in preferences widget"""
        # Update sidebar with fresh data
        self.sidebar.update_username(self.username)
        # Also update profile tab if it exists
        if hasattr(self, 'profile_widget'):
            self.profile_widget.refresh_data()
    
    def update_username(self, username):
        """Update the displayed username"""
        self.username = username
        
        # Get user data from database
        self.user_data = self.db_handler.get_user_data(username)
        self.fullname = self.user_data.get('fullname', username) if self.user_data else username
        
        # Update sidebar
        self.sidebar.update_username(username)
        
        # Update profile widget
        self.profile_widget.update_username(username)
        
        # Update preferences widget
        self.prefs_widget.update_username(username)