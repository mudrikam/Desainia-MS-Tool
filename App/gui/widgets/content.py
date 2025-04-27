from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import Qt
from .pages.settings_page import SettingsPage
from .pages.home_page import HomePage
from .header import PageHeaderWidget

class ContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(0)
        
        # Add header (keep at edge)
        self.header = PageHeaderWidget()
        self.layout.addWidget(self.header)
        
        # Create stacked widget with padding
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.stack)
        
        # Add placeholder pages
        self.pages = {}
        self._add_default_pages()
    
    def _add_default_pages(self):
        """Add default pages to the stack"""
        pages = {
            'home': HomePage(),
            'settings': SettingsPage()
        }
        
        for name, widget in pages.items():
            self.add_page(name, widget)
    
    def add_page(self, name, widget):
        """Add a new page to the stack"""
        self.pages[name] = self.stack.count()
        self.stack.addWidget(widget)
    
    def show_page(self, name):
        """Switch to specified page"""
        if name in self.pages:
            self.stack.setCurrentIndex(self.pages[name])
