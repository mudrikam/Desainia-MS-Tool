from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

class PageHeaderWidget(QFrame):
    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)
        
        # Main horizontal layout for frames
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create 3 empty frames
        for i in range(3):
            content_frame = QFrame()
            content_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(127, 127, 127, 0.1);
                    border-radius: 10px;
                }
            """)
            layout.addWidget(content_frame)

    # Remove unused methods
    def set_title(self, text): pass
    def set_description(self, text): pass
