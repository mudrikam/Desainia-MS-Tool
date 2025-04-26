from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QProgressBar, QWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
import qtawesome as qta

class UpdateDialog(QDialog):
    def __init__(self, current_version, new_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Available")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Icon and title
        header = QWidget()
        header_layout = QHBoxLayout(header)
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.sync-alt', color='#0366d6').pixmap(32, 32))
        title = QLabel(f"Update Available: v{new_version}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Info text
        info = QLabel(
            f"Current version: v{current_version}\n"
            f"New version: v{new_version}\n\n"
            "The application will:\n"
            "• Download the new version\n"
            "• Replace current files with new version\n"
            "• Restart automatically\n\n"
            "Note: Your database and settings will not be affected."
        )
        info.setWordWrap(True)
        
        # Progress bar (hidden initially)
        self.progress = QProgressBar()
        self.progress.hide()
        
        # Buttons
        buttons = QWidget()
        button_layout = QHBoxLayout(buttons)
        self.update_btn = QPushButton("Update Now")
        self.update_btn.setStyleSheet("background-color: #0366d6; color: white; padding: 8px 16px;")
        cancel_btn = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.update_btn)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(info)
        layout.addWidget(self.progress)
        layout.addWidget(buttons)
        
        # Connect buttons
        cancel_btn.clicked.connect(self.reject)
