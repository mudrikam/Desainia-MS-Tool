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
        home = self.addItem("fa5s.th", "Home", top_layout)  # Changed from fa5s.home to fa5s.th
        home.clicked.connect(self.home_clicked)
        
        analytics = self.addItem("fa5s.chart-bar", "Analytics", top_layout)
        analytics.clicked.connect(self.analytics_clicked)
        
        files = self.addItem("fa5s.folder", "Files", top_layout)
        files.clicked.connect(self.files_clicked)
        
        # Add settings to bottom
        settings = self.addItem("fa5s.cog", "Settings", bottom_layout)
        settings.clicked.connect(self.settings_clicked)
        
    def addItem(self, icon_name, tooltip="", parent_layout=None):
        """Add an icon button"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        btn = QPushButton()
        icon = qta.icon(icon_name, color=QApplication.palette().text().color().name())
        btn.setIcon(icon)
        btn.setIconSize(btn.sizeHint() * 0.8)  # Make icon 80% of original size
        btn.setToolTip(tooltip)  # Add tooltip to button instead
        
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
        
        if parent_layout is not None:
            parent_layout.addWidget(container)
        return btn
