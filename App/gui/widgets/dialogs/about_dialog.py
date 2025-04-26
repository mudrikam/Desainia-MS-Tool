from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
import qtawesome as qta
import os

class AboutDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Desainia MS Tool")
        self.setMinimumWidth(400)
        self.setFixedHeight(380)  # Increased height for requirements
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title only (removed icon)
        title = QLabel("Desainia MS Tool")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Version info with requirements
        requirements = self._get_requirements()
        req_text = "\n".join(f"• {name} {version}" for name, version in requirements)
        version_info = QLabel(
            f"Version: {config['application']['version']}\n"
            f"Python: {config['runtime']['python_version']}\n\n"
            f"Package Requirements:\n{req_text}"
        )
        version_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Copyright
        copyright_label = QLabel("© 2025 Desainia Studio\nAll rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # License
        license_label = QLabel("Licensed under GNU General Public License v3.0")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Close button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        button_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(version_info)
        layout.addWidget(copyright_label)
        layout.addWidget(license_label)
        layout.addWidget(button_container)
        
        # Connect button
        close_btn.clicked.connect(self.accept)

    def _get_requirements(self):
        """Parse requirements.txt and return list of (package, version) tuples"""
        requirements = []
        try:
            req_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'requirements.txt')
            with open(req_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Handle ==, >=, <= version specifiers
                        parts = line.replace('>=', '≥').replace('==', ' ').replace('<=', '≤').split(None, 1)
                        if len(parts) == 2:
                            requirements.append(parts)
                        else:
                            requirements.append((parts[0], ''))
        except Exception as e:
            print(f"Error reading requirements: {e}")
            return [("Error", "reading requirements")]
        return requirements
