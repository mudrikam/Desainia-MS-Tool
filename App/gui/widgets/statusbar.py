from PyQt6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices, QColor
from PyQt6.QtCore import QUrl
from ...utils.updater import UpdateChecker
import qtawesome as qta

class StatusBar(QStatusBar):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        # Add border and padding
        self.setStyleSheet("""
            QStatusBar {
                border-top: 1px solid palette(dark);
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
        commit_icon_pixmap = qta.icon('fa5s.code-branch').pixmap(14, 14)
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
        github_icon_pixmap = qta.icon('fa5b.github').pixmap(14, 14)
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
        coffee_icon_pixmap = qta.icon('fa5s.mug-hot').pixmap(14, 14)
        self.coffee_icon.setPixmap(coffee_icon_pixmap)
        self.coffee_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.coffee_container.mousePressEvent = self.open_coffee
        
        coffee_layout.addWidget(self.coffee_icon)
        
        # Add permanent widgets to right side
        self.addPermanentWidget(python_version)
        self.addPermanentWidget(self.update_container)
        self.addPermanentWidget(self.app_version)
        self.addPermanentWidget(self.commit_container)
        self.addPermanentWidget(self.github_container)
        self.addPermanentWidget(self.coffee_container)
        
        # Start update checker
        self.checker = UpdateChecker(config['application']['version'])
        self.checker.update_available.connect(self.show_update)
        self.checker.start()
    
    def show_update(self, new_version):
        bell_icon = qta.icon('fa5s.bell', color='#0095FF').pixmap(12, 12)
        self.update_icon.setPixmap(bell_icon)
        self.update_text.setText(f"Update to v{new_version}")
        self.update_container.setVisible(True)
        self.new_version = new_version
    
    def open_release_page(self, event):
        self.checker.download_and_install(self.new_version)
    
    def open_github_repo(self, event):
        QDesktopServices.openUrl(QUrl("https://github.com/mudrikam/Desainia-MS-Tool"))
    
    def open_coffee(self, event):
        QDesktopServices.openUrl(QUrl("https://www.buymeacoffee.com/mudrikam"))
    
    def open_commit_page(self, event):
        commit_hash = self.commit_text.text()
        if commit_hash:
            QDesktopServices.openUrl(QUrl(f"https://github.com/mudrikam/Desainia-MS-Tool/commit/{commit_hash}"))
