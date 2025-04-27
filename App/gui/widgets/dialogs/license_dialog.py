from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt
import os

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation  # Translation helper
        
        self.setWindowTitle(self.tr('dialog', 'license', 'title'))
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # Create text edit for license content
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.text_edit)
        
        # Add close button
        button_container = QHBoxLayout()
        close_btn = QPushButton(self.tr('dialog', 'license', 'close'))
        close_btn.setFixedWidth(100)
        button_container.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_container)
        
        # Load license text
        self._load_license()
        
        # Connect button
        close_btn.clicked.connect(self.accept)
        
    def _load_license(self):
        """Load and display license text from LICENSE.txt"""
        try:
            license_path = os.path.join(os.path.dirname(os.path.dirname(
                          os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
                          'LICENSE.txt')
            
            with open(license_path, 'r') as f:
                license_text = f.read()
            self.text_edit.setPlainText(license_text)
        except Exception as e:
            self.text_edit.setPlainText(f"Error loading license file: {str(e)}")
