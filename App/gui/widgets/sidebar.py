from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFrame, QPushButton, 
                            QApplication, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import qtawesome as qta
import os
import webbrowser
import platform
import subprocess
import json
from .dialogs.about_dialog import AboutDialog  # Add this import

class SideBar(QFrame):
    # Update signals - remove analytics_clicked
    home_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load config
        app = QApplication.instance()
        config_path = app.BASE_DIR.get_path('App', 'config', 'config.json')
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.setObjectName("SideBar")
        self.active_button = None  # Track active button
        
        self.setFixedWidth(60)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content widget
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(content)

        # Use system colors
        palette = QApplication.palette()
        self.setStyleSheet(f"""
            QFrame#SideBar {{
                border-right: 1px solid rgba(0, 0, 0, 0.08);
                background-color: rgba(0, 0, 0, 0.05);
            }}
            QPushButton {{
                padding: 8px;
                border: none;
                border-radius: 4px;
                margin: 2px;
                background: transparent;
            }}
            QPushButton[active="true"] {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
        """)
        
        # Create top section for main icons
        self.top_section = QWidget()
        top_layout = QVBoxLayout(self.top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Create bottom section for settings
        self.bottom_section = QWidget()
        bottom_layout = QVBoxLayout(self.bottom_section)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Add sections to main layout
        self.content_layout.addWidget(self.top_section)
        self.content_layout.addStretch()
        self.content_layout.addWidget(self.bottom_section)
        
        # Add top icons
        self.home_btn = self.addItem("fa6s.house", "Home", top_layout)
        self.home_btn.clicked.connect(self._on_home_clicked)
        
        self.github_btn = self.addItem("fa6b.github", "Visit GitHub", top_layout)
        self.github_btn.clicked.connect(self._on_github_clicked)
        
        self.bug_btn = self.addItem("fa6s.bug", "Report Bug", top_layout)
        self.bug_btn.clicked.connect(self._on_bug_clicked)
        
        self.files_btn = self.addItem("fa6s.folder", "Open App Folder", top_layout)
        self.files_btn.clicked.connect(self._on_files_clicked)
        
        # Add settings and about to bottom
        self.about_btn = self.addItem("fa6s.circle-info", "About", bottom_layout)
        self.about_btn.clicked.connect(self._on_about_clicked)
        
        self.settings_btn = self.addItem("fa6s.gear", "Settings", bottom_layout)
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        
        # Set home as default active
        self._set_active(self.home_btn)

    def _set_active(self, button):
        """Set active state for button"""
        if self.active_button:
            self.active_button.setProperty("active", False)
            self.active_button.style().unpolish(self.active_button)
            self.active_button.style().polish(self.active_button)
        self.active_button = button
        button.setProperty("active", True)
        button.style().unpolish(button)
        button.style().polish(button)

    def _on_home_clicked(self):
        self._set_active(self.home_btn)
        self.home_clicked.emit()
        
    def _on_files_clicked(self):
        """Open base directory in system file explorer"""
        app = QApplication.instance()
        base_dir = app.BASE_DIR.get_path()
        system = platform.system()

        try:
            if system == 'Windows':
                os.startfile(base_dir)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', base_dir])
            else:  # Linux and others
                subprocess.run(['xdg-open', base_dir])
        except Exception as e:
            print(f"Error opening folder: {str(e)}")
        
    def _on_settings_clicked(self):
        self._set_active(self.settings_btn)
        self.settings_clicked.emit()
        
    def _on_github_clicked(self):
        """Open GitHub repository"""
        webbrowser.open('https://github.com/mudrikam/Desainia-Rak-Arsip')
        
    def _on_bug_clicked(self):
        """Open GitHub issues page"""
        webbrowser.open('https://github.com/mudrikam/Desainia-Rak-Arsip/issues')
    
    def _on_about_clicked(self):
        """Show about dialog"""
        dialog = AboutDialog(self.config, self)
        dialog.exec()

    def addItem(self, icon_name, tooltip="", parent_layout=None):
        """Add an icon button"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        btn = QPushButton()
        icon = qta.icon(icon_name, color=QApplication.palette().text().color().name())

        btn.setIcon(icon)
        btn.setIconSize(btn.sizeHint() * 0.8)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
        
        if parent_layout is not None:
            parent_layout.addWidget(container)
        return btn
