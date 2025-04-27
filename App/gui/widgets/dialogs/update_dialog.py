from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QProgressBar, QWidget, QHBoxLayout, QTextEdit, QApplication)
from PyQt6.QtCore import Qt, QTimer
import qtawesome as qta
import random
import json
import os

class UpdateDialog(QDialog):
    def __init__(self, current_version, new_version, release_notes, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)  # Disable close button
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation
        self.setContentsMargins(20, 20, 20, 20)
        
        # Load release messages based on language
        config_path = self.app.BASE_DIR.get_path('App', 'config', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        language = config.get('application', {}).get('language', 'en')
        message_path = self.app.BASE_DIR.get_path('App', 'config', f'release_message_{language}.json')
        
        try:
            with open(message_path, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        except FileNotFoundError:
            # Fallback to English if language file not found
            fallback_path = self.app.BASE_DIR.get_path('App', 'config', 'release_message_en.json')
            with open(fallback_path, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
        
        self.setWindowTitle(random.choice(self.messages['release_titles']))
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Icon and title
        header = QWidget()
        header_layout = QHBoxLayout(header)
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa6s.arrow-rotate-right', color='#0366d6').pixmap(32, 32))
        
        # Title formatting dengan emoji tetap terjaga
        greeting = random.choice(self.messages['greetings'])
        version_msg = random.choice(self.messages['version_messages']).format(version=new_version)
        title = QLabel(f"{greeting}\n{version_msg}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Info text dengan semua elemen terpisah jelas
        current_ver = random.choice(self.messages['current_version_messages']).format(version=current_version)
        new_ver = random.choice(self.messages['version_messages']).format(version=new_version)
        fact = random.choice(self.messages['facts'])
        info = QLabel(f"{current_ver}\n{new_ver}\n\n{fact}\n")
        info.setWordWrap(True)
        
        # Release notes
        notes_label = QLabel(self.tr('dialog', 'update', 'release_notes'))
        notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setMinimumHeight(150)
        self.notes.setMaximumHeight(300)
        if release_notes and release_notes.strip():
            self.notes.setPlainText(release_notes.strip())
        else:
            self.notes.setPlainText(self.tr('dialog', 'update', 'no_notes'))
        self.notes.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Timer label with translations
        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(f"color: {self.tr('dialog', 'update', 'countdown_color')}; font-weight: bold;")
        
        # Get random countdown message template once
        self.countdown_template = random.choice(self.messages['countdown_messages'])
        self.timer_label.setText(self.countdown_template.format(count=30))
        
        # Setup countdown timer
        self.countdown = 30
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1 second
        self.timer.timeout.connect(self._update_countdown)
        self.timer.start()
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.hide()
        
        # Buttons styling from translations
        buttons = QWidget()
        button_layout = QHBoxLayout(buttons)
        button_layout.setContentsMargins(0, 10, 0, 0)  # Add top margin
        
        # Cancel button with local styles
        self.cancel_btn = QPushButton(random.choice(self.messages['later_messages']).strip())
        self.cancel_btn.setMinimumWidth(120)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(button);
                color: palette(buttonText);
            }
            QPushButton:hover {
                background-color: palette(light);
            }
            QPushButton:disabled {
                background-color: palette(dark);
            }
        """)
        
        # Update button with local styles
        self.update_btn = QPushButton(random.choice(self.messages['update_now_messages']).strip())
        self.update_btn.setMinimumWidth(120)
        self.update_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0256b9;
            }
        """)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.update_btn)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(info)
        layout.addWidget(notes_label)
        layout.addWidget(self.notes)
        layout.addWidget(self.timer_label)  # Add timer label
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addWidget(buttons)
        
        # Connect buttons
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setEnabled(False)  # Initially disabled

    def _update_countdown(self):
        if self.countdown > 0:
            self.timer_label.setText(self.countdown_template.format(count=self.countdown))
            self.countdown -= 1
        else:
            self.timer.stop()
            self.timer_label.setText(self.tr('dialog', 'update', 'countdown_done'))
            self.timer_label.setStyleSheet(f"color: {self.tr('dialog', 'update', 'countdown_done_color')}; font-weight: 600;")
            self.cancel_btn.setEnabled(True)

    def closeEvent(self, event):
        # Prevent closing while timer is running
        if self.countdown > 0:
            event.ignore()
        else:
            self.timer.stop()
            super().closeEvent(event)
