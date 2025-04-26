from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFrame, QPushButton, 
                            QApplication, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import qtawesome as qta

class SideBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SideBar")
        
        # Set fixed width for sidebar
        self.setFixedWidth(80)
        
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
                padding: 12px;
                border: none;
                border-radius: 4px;
                margin: 2px 8px;
                background: transparent;
            }}
            QPushButton:hover {{
                background: {palette.alternateBase().color().name()};
            }}
            QLabel {{
                color: {palette.text().color().name()};
                font-size: 10px;
                margin-top: -8px;
                margin-bottom: 8px;
            }}
        """)
        
        # Add default icons with labels
        self.addItem("fa5s.home", "Home")
        self.addItem("fa5s.chart-bar", "Analytics")
        self.addItem("fa5s.cog", "Settings")
        self.addItem("fa5s.folder", "Files")
        
        # Add stretch to push icons to top
        self.content_layout.addStretch()
        
    def addItem(self, icon_name, tooltip=""):
        """Add an icon button with label below it"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        btn = QPushButton()
        icon = qta.icon(icon_name, color=QApplication.palette().text().color().name())
        btn.setIcon(icon)
        btn.setIconSize(btn.sizeHint())
        
        label = QLabel(tooltip)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignHCenter)
        
        self.content_layout.addWidget(container)
        return container
