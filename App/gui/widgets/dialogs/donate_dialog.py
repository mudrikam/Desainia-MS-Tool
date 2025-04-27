from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import qtawesome as qta

class DonateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation
        
        self.setWindowTitle(self.tr('dialog', 'donate', 'title'))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title with heart icon
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.heart', color='#FF335F').pixmap(32, 32))
        icon_label.setStyleSheet("background: transparent;")
        title = QLabel(self.tr('dialog', 'donate', 'header'))
        title.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title)
        
        # Support message
        message = QLabel(self.tr('dialog', 'donate', 'message'))
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: gray; padding: 10px; background: transparent;")
        message.setWordWrap(True)
        
        # QRIS Section 
        qris_section = QWidget()
        qris_layout = QVBoxLayout(qris_section)
        qris_section.setLayout(qris_layout)
        
        # QRIS image
        qris_label = QLabel()
        qris_path = self.app.BASE_DIR.get_path('App', 'resources', 'proprietary', 'img', 'qris.jpeg')
        pixmap = QPixmap(qris_path)
        if not pixmap.isNull():
            if pixmap.width() > 400:
                pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            qris_label.setPixmap(pixmap)
        else:
            qris_label.setText("Error loading QRIS code")
        qris_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # QRIS instructions
        instructions = QLabel(self.tr('dialog', 'donate', 'qris_instruction'))
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: gray;")
        
        qris_layout.addWidget(qris_label)
        qris_layout.addWidget(instructions)
        
        # Add widgets to layout
        layout.addWidget(title_widget)
        layout.addWidget(message)
        layout.addWidget(qris_section)
