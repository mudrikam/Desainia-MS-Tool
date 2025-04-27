from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QWidget, QHBoxLayout, QTextEdit, QApplication)
from PyQt6.QtCore import Qt
import qtawesome as qta
import os
from .about_details_dialog import AboutDetailsDialog

class AboutDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation  # Translation helper
        
        self.setWindowTitle(f"{self.tr('dialog', 'about', 'title')} {config['application']['name']}")
        self.setMinimumWidth(400)
        self.setFixedHeight(380)  # Increased height for requirements
        
        # Add system-based styling
        self.setStyleSheet("""
            QDialog {
                background-color: palette(window);
                color: palette(windowText);
            }
            QPushButton {
                padding: 5px 15px;
                border: none;
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(button);
                color: palette(buttonText);
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: palette(light);
            }
            QPushButton:pressed {
                background-color: palette(dark);
            }
            QLabel {
                color: palette(text);
            }
            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title from config
        title = QLabel(config['application']['name'])
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Version info with requirements
        requirements = self._get_requirements()
        req_text = "\n".join(f"• {name} {version}" for name, version in requirements)
        
        version_label = QLabel()
        version_label.setText(
            f'<div style="text-align: center;">'
            f'<span style="font-size: 18px; font-weight: 600;">{self.tr("dialog", "about", "version")}: {config["application"]["version"]}</span>'
            f'<br>'
            f'Python: {config["runtime"]["python_version"]}'
            f'</div>'
        )
        version_label.setTextFormat(Qt.TextFormat.RichText)
        
        # Requirements in scrollable text edit
        req_edit = QTextEdit()
        req_edit.setReadOnly(True)
        req_edit.setFixedHeight(120)
        req_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        req_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        req_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        req_edit.setText(f"{self.tr('dialog', 'about', 'requirements')}:\n{req_text}")
        
        # Add spacing widget before copyright
        spacing = QWidget()
        spacing.setFixedHeight(20)  # Increased from 10 to 20
        
        # Container for copyright and license
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(10, 10, 10, 10)
        
        # Copyright with organization from config
        copyright_label = QLabel(f"{self.tr('dialog', 'about', 'author')}: {config['application']['author']}\n{self.tr('dialog', 'about', 'rights')}")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # License
        license_label = QLabel(self.tr('dialog', 'about', 'license'))
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info_layout.addWidget(copyright_label)
        info_layout.addWidget(license_label)
        
        # Button container with Thanks To and Details
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        thanks_btn = QPushButton(f" {self.tr('dialog', 'about', 'thanks_to')}")
        thanks_btn.setIcon(qta.icon('fa6s.heart', color='#FF335F'))
        details_btn = QPushButton(self.tr('dialog', 'about', 'details'))
        thanks_btn.setFixedWidth(100)
        details_btn.setFixedWidth(100)
        button_layout.addWidget(thanks_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(details_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(version_label)
        layout.addWidget(req_edit)
        layout.addWidget(spacing)
        layout.addWidget(info_container)
        layout.addWidget(button_container)
        
        # Connect buttons
        thanks_btn.clicked.connect(self.show_credits)
        details_btn.clicked.connect(self.show_details)

    def show_credits(self):
        """Show credits dialog"""
        credits_dialog = QDialog(self)
        credits_dialog.setWindowTitle(self.tr('dialog', 'about', 'credits'))
        credits_dialog.setMinimumWidth(500)
        credits_dialog.setMinimumHeight(400)
        
        # Apply same styling to credits dialog
        credits_dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(credits_dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        app = QApplication.instance()
        credits_path = app.BASE_DIR.get_path('CREDITS.TXT')
        
        try:
            with open(credits_path, 'r') as f:
                text_edit.setPlainText(f.read())
        except Exception as e:
            text_edit.setPlainText(f"Error loading credits: {str(e)}")
        
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton(self.tr('dialog', 'about', 'close'))
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(credits_dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        credits_dialog.exec()

    def show_details(self):
        """Show about details dialog"""
        dialog = AboutDetailsDialog(self)
        dialog.exec()

    def _get_requirements(self):
        """Parse requirements.txt and return list of (package, version) tuples"""
        requirements = []
        try:
            app = QApplication.instance()
            req_path = app.BASE_DIR.get_path('requirements.txt')
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
