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
        self.app_version = QLabel(f"App v{config['application']['version']}")
        
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
        
        # Add permanent widgets to right side
        self.addPermanentWidget(python_version)
        self.addPermanentWidget(self.update_container)
        self.addPermanentWidget(self.app_version)
        
        # Start update checker
        self.checker = UpdateChecker(config['application']['version'])
        self.checker.update_available.connect(self.show_update)
        self.checker.start()
    
    def show_update(self, new_version):
        bell_icon = qta.icon('fa5s.bell', color='#0366d6').pixmap(12, 12)
        self.update_icon.setPixmap(bell_icon)
        self.update_text.setText(f"Update to v{new_version}")
        self.update_container.setVisible(True)
        self.new_version = new_version
    
    def open_release_page(self, event):
        self.checker.download_and_install(self.new_version)
