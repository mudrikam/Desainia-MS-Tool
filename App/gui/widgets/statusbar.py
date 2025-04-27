from PyQt6.QtWidgets import (QStatusBar, QLabel, QHBoxLayout, QWidget, 
                            QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices, QColor
from PyQt6.QtCore import QUrl
import json
from ...utils.updater import UpdateChecker
import qtawesome as qta
from .dialogs.donate_dialog import DonateDialog

class StatusBar(QStatusBar):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        
        # Add border and padding
        self.setStyleSheet("""
            QStatusBar {
                border-top: 1px solid rgba(0, 0, 0, 0.08);
                background-color: rgba(0, 0, 0, 0.05);
                padding: 3px 10px;
            }
            QStatusBar QLabel {
                margin: 2px 3px;
            }
        """)
        
        # Create version labels
        self.app_version = QLabel(f"v{config['application']['version']}")
        
        # Create commit hash container
        self.commit_container = QWidget()
        commit_layout = QHBoxLayout(self.commit_container)
        commit_layout.setContentsMargins(0, 0, 0, 0)
        commit_layout.setSpacing(2)
        
        self.commit_icon = QLabel()
        commit_icon_pixmap = qta.icon('fa6s.code-commit').pixmap(14, 14)
        self.commit_icon.setPixmap(commit_icon_pixmap)
        
        self.commit_text = QLabel(config.get('git', {}).get('commit_hash', ''))
        self.commit_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.commit_container.mousePressEvent = self.open_commit_page
        
        commit_layout.addWidget(self.commit_icon)
        commit_layout.addWidget(self.commit_text)

        # Create update label with container
        self.update_container = QWidget()
        self.update_container.setVisible(False)
        update_layout = QHBoxLayout(self.update_container)
        update_layout.setContentsMargins(0, 0, 0, 0)
        update_layout.setSpacing(2)
        
        self.update_icon = QLabel()
        self.update_text = QLabel()
        self.update_text.setStyleSheet("color: #0366d6;")
        self.update_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_container.mousePressEvent = self.open_release_page
        
        update_layout.addWidget(self.update_icon)
        update_layout.addWidget(self.update_text)
        
        python_version = QLabel(f"Python {config['runtime']['python_version']}")
        
        # Create GitHub icon
        self.github_container = QWidget()
        github_layout = QHBoxLayout(self.github_container)
        github_layout.setContentsMargins(0, 0, 0, 0)
        github_layout.setSpacing(2)
        
        self.github_icon = QLabel()
        github_icon_pixmap = qta.icon('fa6b.github').pixmap(14, 14)
        self.github_icon.setPixmap(github_icon_pixmap)
        self.github_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_container.mousePressEvent = self.open_github_repo
        
        github_layout.addWidget(self.github_icon)
        
        # Create Coffee icon
        self.coffee_container = QWidget()
        coffee_layout = QHBoxLayout(self.coffee_container)
        coffee_layout.setContentsMargins(0, 0, 0, 0)
        coffee_layout.setSpacing(2)
        
        self.coffee_icon = QLabel()
        coffee_icon_pixmap = qta.icon('fa6s.mug-hot').pixmap(14, 14)
        self.coffee_icon.setPixmap(coffee_icon_pixmap)
        self.coffee_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.coffee_container.mousePressEvent = self.open_coffee
        
        coffee_layout.addWidget(self.coffee_icon)
        
        # Create WhatsApp icon
        self.wa_container = QWidget()
        wa_layout = QHBoxLayout(self.wa_container)
        wa_layout.setContentsMargins(0, 0, 0, 0)
        wa_layout.setSpacing(2)
        
        self.wa_icon = QLabel()
        wa_icon_pixmap = qta.icon('fa6b.whatsapp').pixmap(14, 14)
        self.wa_icon.setPixmap(wa_icon_pixmap)
        self.wa_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.wa_container.mousePressEvent = self.open_whatsapp
        
        wa_layout.addWidget(self.wa_icon)
        
        # Create heart icon
        self.heart_container = QWidget()
        heart_layout = QHBoxLayout(self.heart_container)
        heart_layout.setContentsMargins(0, 0, 0, 0)
        heart_layout.setSpacing(2)
        
        self.heart_icon = QLabel()
        heart_icon_pixmap = qta.icon('fa6s.heart', color='#FF335F').pixmap(14, 14)
        self.heart_icon.setPixmap(heart_icon_pixmap)
        self.heart_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.heart_container.mousePressEvent = self.show_donate
        
        heart_layout.addWidget(self.heart_icon)
        
        # Create language toggle container
        self.lang_container = QWidget()
        lang_layout = QHBoxLayout(self.lang_container)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(2)
        
        # Using emoji flags with proper font
        self.lang_label = QLabel()
        self.lang_label.setStyleSheet("QLabel { font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'Segoe UI Symbol'; font-size: 14px; }")
        self.lang_label.setText("🇺🇸" if config['application']['language'] == 'en' else "🇮🇩")
        self.lang_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_container.mousePressEvent = self.toggle_language
        
        lang_layout.addWidget(self.lang_label)
        
        # Add permanent widgets to right side
        self.addPermanentWidget(python_version)
        self.addPermanentWidget(self.update_container)
        self.addPermanentWidget(self.app_version)
        self.addPermanentWidget(self.commit_container)
        self.addPermanentWidget(self.github_container)
        self.addPermanentWidget(self.coffee_container)
        self.addPermanentWidget(self.heart_container)
        self.addPermanentWidget(self.wa_container)
        self.addPermanentWidget(self.lang_container)
        
        # Initialize update checker
        print("\nStatusBar Update Check:")
        print(f"Current app version: v{config['application']['version']}")
        print(f"GitHub Token: {config['repository']['github']['token'][:10]}...")
        print(f"API URL: {config['repository']['github']['releases']}/latest")
        
        try:
            self.update_container.setVisible(False)
            self.checker = UpdateChecker(config['application']['version'])
            self.checker.update_available.connect(self.show_update)
            print("Update checker initialized successfully")
            self.checker.start()
        except Exception as e:
            print(f"Error initializing update checker: {str(e)}")
    
    def show_update(self, new_version, release_notes):
        try:
            print("\nUpdate notification received:")
            print(f"New version available: v{new_version}")
            print(f"Current version: v{self.config['application']['version']}")
            
            self.new_version = new_version
            self.release_notes = release_notes
            # Changed icon to arrow-up from fa6s
            bell_icon = qta.icon('fa6s.arrow-up', color='#0095FF').pixmap(12, 12)
            self.update_icon.setPixmap(bell_icon)
            self.update_text.setText(f"Update to v{new_version}")
            self.update_container.setVisible(True)
            self.update_container.repaint()
            
            print("Update notification shown successfully")
            QApplication.instance().processEvents()
        except Exception as e:
            print(f"Error showing update notification: {str(e)}")
        
    def open_release_page(self, event):
        print(f"\nStarting update process to v{self.new_version}")
        self.checker.download_and_install(self.new_version)
    
    def open_github_repo(self, event):
        QDesktopServices.openUrl(QUrl(self.config['repository']['url']))
    
    def open_coffee(self, event):
        QDesktopServices.openUrl(QUrl("https://www.buymeacoffee.com/mudrikam"))
    
    def open_commit_page(self, event):
        commit_hash = self.commit_text.text()
        if commit_hash:
            QDesktopServices.openUrl(QUrl(f"{self.config['repository']['url']}/commit/{commit_hash}"))
    
    def open_whatsapp(self, event):
        QDesktopServices.openUrl(QUrl(self.config['repository']['whatsapp_url']))
    
    def show_donate(self, event):
        dialog = DonateDialog(self)
        dialog.exec()
    
    def toggle_language(self, event):
        current_lang = self.config['application']['language']
        new_lang = 'id' if current_lang == 'en' else 'en'
        
        # Show restart dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Restart Required")
        msg.setText("The application needs to restart to apply language changes.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            # Save new language setting
            self.config['application']['language'] = new_lang
            with open('App/config/config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            # Get current program path and arguments
            import sys
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(["Launcher.bat"])
            else:
                subprocess.Popen(["./Launcher.sh"])
            
            # Exit current instance
            QApplication.instance().quit()
        
        # Update display even if restart was cancelled
        self.lang_label.setText("🇺🇸" if new_lang == 'en' else "🇮🇩")
