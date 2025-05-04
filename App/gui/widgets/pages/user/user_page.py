from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
import qtawesome as qta

class UserProfilePage(QWidget):
    """User profile page shown after successful login."""
    
    def __init__(self, parent=None, username="User"):
        super().__init__(parent)
        
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
        welcome_label = QLabel(f"Welcome, {username}!")
        welcome_label.setStyleSheet("""
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
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(user_icon)
        header_layout.addLayout(welcome_layout)
        header_layout.addStretch()
        
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
