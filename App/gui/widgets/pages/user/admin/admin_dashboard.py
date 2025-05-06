from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

class AdminDashboard(QWidget):
    """Admin dashboard page shown after successful login for administrators."""
    
    # Add signal for logout
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None, username="Admin"):
        super().__init__(parent)
        self.username = username
        
        # Get app instance 
        self.app = QApplication.instance()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 40, 20, 20)
        main_layout.setSpacing(15)
        
        # Welcome header with admin icon
        header_layout = QHBoxLayout()
        
        admin_icon = QLabel()
        admin_icon.setPixmap(qta.icon("fa6s.user-shield", color="#6200ea").pixmap(64, 64))
        admin_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_layout = QVBoxLayout()
        
        # Welcome message
        self.welcome_label = QLabel(f"Welcome, {username}!")
        self.welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 500;
            color: palette(text);
        """)
        
        # Role label
        self.role_label = QLabel("Administrator Dashboard")
        self.role_label.setStyleSheet("""
            font-size: 16px;
            color: #6200ea;
            font-weight: 500;
        """)
        
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(self.role_label)
        
        header_layout.addWidget(admin_icon)
        header_layout.addLayout(welcome_layout)
        header_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_icon = qta.icon("fa6s.right-from-bracket", color="#dc3545")
        logout_btn.setIcon(logout_icon)
        icon_size = logout_btn.iconSize()
        logout_btn.setIconSize(icon_size * 0.7)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #dc3545;
                border: 1px solid #dc3545;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
                font-weight: 500;
                outline: none;
            }
            QPushButton:focus {
                outline: none;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.2);
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self._on_logout)
        
        header_layout.addWidget(logout_btn)
        
        # Admin dashboard content placeholder
        content_label = QLabel("This will be the admin dashboard content with administrative controls.")
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setStyleSheet("""
            font-size: 16px;
            color: palette(text);
            background-color: rgba(98, 0, 234, 0.05);
            border-radius: 8px;
            padding: 30px;
            margin: 20px 0;
        """)
        
        # Add all components to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(content_label)
        main_layout.addStretch()
    
    def _on_logout(self):
        """Handle logout button click"""
        # Import auth helper and logout
        from App.core.user._user_auth import UserAuth
        auth = UserAuth(self.app)
        
        # Get current user before logout
        current_user = auth.get_current_user()
        if current_user:
            print(f"Logging out admin: {current_user.get('username', 'unknown')}")
        
        # Ensure remember_login is disabled
        auth.update_settings(remember_login=False)
        
        # Perform the logout
        auth.logout()
        
        # Emit signal to notify parent
        self.logout_requested.emit()
    
    def update_username(self, username):
        """Update the displayed username"""
        self.username = username
        self.welcome_label.setText(f"Welcome, {username}!")