from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFrame, QPushButton, 
                            QApplication, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import qtawesome as qta

class SideBar(QFrame):
    # Add signals
    home_clicked = pyqtSignal()
    analytics_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    files_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
                background: {palette.base().color().name()};
                border-right: 1px solid {palette.dark().color().name()};
            }}
            QPushButton {{
                padding: 8px;
                border: none;
                border-radius: 4px;
                margin: 2px;
                background: transparent;
            }}
            QPushButton[active="true"] {{
                background: {palette.alternateBase().color().name()};
            }}
            QPushButton:hover {{
                background: {palette.alternateBase().color().name()};
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
        self.home_btn = self.addItem("fa5s.th", "Home", top_layout)
        self.home_btn.clicked.connect(self._on_home_clicked)
        
        self.analytics_btn = self.addItem("fa5s.chart-bar", "Analytics", top_layout)
        self.analytics_btn.clicked.connect(self._on_analytics_clicked)
        
        self.files_btn = self.addItem("fa5s.folder", "Files", top_layout)
        self.files_btn.clicked.connect(self._on_files_clicked)
        
        # Add settings to bottom
        self.settings_btn = self.addItem("fa5s.cog", "Settings", bottom_layout)
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
        
    def _on_analytics_clicked(self):
        self._set_active(self.analytics_btn)
        self.analytics_clicked.emit()
        
    def _on_files_clicked(self):
        self._set_active(self.files_btn)
        self.files_clicked.emit()
        
    def _on_settings_clicked(self):
        self._set_active(self.settings_btn)
        self.settings_clicked.emit()
        
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
        
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
        
        if parent_layout is not None:
            parent_layout.addWidget(container)
        return btn
