from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class AttendanceTool(QWidget):
    """Attendance tracking tool for team members."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title label
        title = QLabel("Attendance")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: palette(text);
            margin-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Placeholder text
        placeholder = QLabel("Attendance tracking tool - Coming soon")
        placeholder.setStyleSheet("""
            font-size: 16px;
            color: palette(text);
            margin: 40px 0;
        """)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(placeholder)
        layout.addStretch()
