from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

class UserProfilePage(QWidget):
    """User profile page shown after successful login."""
    
    # Add signal for logout
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None, username="User"):
        super().__init__(parent)
        self.username = username
        
        # Get app instance 
        self.app = QApplication.instance()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 40, 20, 20)
        main_layout.setSpacing(15)
        
        # Welcome header with user icon
        header_layout = QHBoxLayout()
        
        user_icon = QLabel()
        user_icon.setPixmap(qta.icon("fa6s.circle-user", color="#0366d6").pixmap(64, 64))
        user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_layout = QVBoxLayout()
        
        # Welcome message
        self.welcome_label = QLabel(f"Welcome, {username}!")
        self.welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 500;
            color: palette(text);
        """)
        
        # Subtitle
        subtitle_label = QLabel("Your account dashboard")
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: palette(mid);
        """)
        
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(user_icon)
        header_layout.addLayout(welcome_layout)
        header_layout.addStretch()
        
        # Logout button with adjusted margins and reversed color scheme
        logout_btn = QPushButton("Logout")
        logout_icon = qta.icon("fa6s.right-from-bracket", color="#dc3545")  # Red icon
        logout_btn.setIcon(logout_icon)
        # Fix: Use a fixed size instead of calculating based on sizeHint
        icon_size = logout_btn.iconSize()
        logout_btn.setIconSize(icon_size * 0.7)  # Slightly smaller icon
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #dc3545;  /* Red text */
                border: 1px solid #dc3545;  /* Red border */
                border-radius: 5px;
                padding: 5px 10px;  /* Reasonable padding for compact look */
                font-size: 14px;
                font-weight: 500;
                outline: none; /* Remove focus outline */
            }
            QPushButton:focus {
                outline: none; /* Remove focus outline */
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 0.1);  /* Light red background on hover */
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.2);  /* Slightly darker red on press */
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self._on_logout)
        
        header_layout.addWidget(logout_btn)
        
        # Information message
        info_label = QLabel("This is your user dashboard. Your account information and preferences will be displayed here.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            font-size: 14px;
            color: palette(text);
            background-color: rgba(0, 0, 0, 0.05);
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        """)
        
        # Stats container
        stats_container = QWidget()
        stats_container.setObjectName("stats_container")
        stats_container.setStyleSheet("""
            QWidget#stats_container {
                background-color: rgba(0, 0, 0, 0.02);
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        
        stats_title = QLabel("Activity Statistics")
        stats_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: palette(text);
            margin-bottom: 10px;
        """)
        
        stats_content = QLabel("No activity recorded yet. Start using the tools to see your statistics here.")
        stats_content.setStyleSheet("""
            font-size: 14px;
            color: palette(mid);
            margin: 10px 0;
        """)
        
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(stats_content)
        
        # Add all components to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(info_label)
        main_layout.addWidget(stats_container)
        main_layout.addStretch()
    
    def _on_logout(self):
        """Handle logout button click"""
        # Import auth helper and logout
        from App.core.user._user_auth import UserAuth
        auth = UserAuth(self.app)
        
        # Get current user before logout
        current_user = auth.get_current_user()
        if current_user:
            print(f"Logging out user: {current_user.get('username', 'unknown')}")
        else:
            print("No user currently logged in")
        
        # Ensure remember_login is disabled
        auth.update_settings(remember_login=False)
        
        # Perform the logout
        success = auth.logout()
        
        # Double check current user is None
        if auth.get_current_user() is not None:
            print("Warning: Current user still not None after logout!")
            auth.current_user = None
        
        # Emit signal to notify parent
        self.logout_requested.emit()
    
    def update_username(self, username):
        """Update the displayed username"""
        self.username = username
        self.welcome_label.setText(f"Welcome, {username}!")
