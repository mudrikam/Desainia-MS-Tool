from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import qtawesome as qta

class DonateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Support Desainia MS Tool")
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
        title = QLabel("Support the Development")
        title.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title)
        
        # Support message
        message = QLabel(
            "\"When a person dies, their deeds come to an end except for three: "
            "Sadaqah Jariyah (continuing charity), beneficial knowledge, "
            "or a righteous child who prays for them.\" - (Sahih Muslim)\n\n"
            "Support this tool as a form of Sadaqah Jariyah."
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: gray; padding: 10px; background: transparent;")
        message.setWordWrap(True)
        
        # QRIS Section 
        qris_section = QWidget()
        qris_layout = QVBoxLayout(qris_section)
        qris_section.setLayout(qris_layout)
        
        # QRIS image
        qris_label = QLabel()
        app = QApplication.instance()
        qris_path = app.BASE_DIR.get_path('App', 'resources', 'proprietary', 'img', 'qris.jpeg')
        pixmap = QPixmap(qris_path)
        if not pixmap.isNull():
            if pixmap.width() > 400:
                pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            qris_label.setPixmap(pixmap)
        else:
            qris_label.setText("Error loading QRIS code")
        qris_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # QRIS instructions
        instructions = QLabel("Scan QRIS code using your mobile banking or e-wallet app")
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: gray;")
        
        qris_layout.addWidget(qris_label)
        qris_layout.addWidget(instructions)
        
        # Add widgets to layout
        layout.addWidget(title_widget)
        layout.addWidget(message)
        layout.addWidget(qris_section)
