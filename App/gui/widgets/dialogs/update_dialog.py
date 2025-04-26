from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QProgressBar, QWidget, QHBoxLayout, QTextEdit)
from PyQt6.QtCore import Qt
import qtawesome as qta

class UpdateDialog(QDialog):
    def __init__(self, current_version, new_version, release_notes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Available")
        self.setMinimumWidth(500)
        
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
        
        # Release notes
        notes_label = QLabel("Release Notes:")
        notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setMinimumHeight(150)
        self.notes.setMaximumHeight(300)
        if release_notes and release_notes.strip():
            self.notes.setPlainText(release_notes.strip())
        else:
            self.notes.setPlainText("No release notes available.")
        self.notes.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.hide()
        
        # Buttons
        buttons = QWidget()
        button_layout = QHBoxLayout(buttons)
        self.update_btn = QPushButton("Update Now")
        cancel_btn = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.update_btn)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(info)
        layout.addWidget(notes_label)
        layout.addWidget(self.notes)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addWidget(buttons)
        
        # Connect buttons
        cancel_btn.clicked.connect(self.reject)
