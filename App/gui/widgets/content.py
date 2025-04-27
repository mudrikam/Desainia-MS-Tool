from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import Qt
from .pages.settings_page import SettingsPage
from .header import PageHeaderWidget

class ContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(0)
        
        # Add header (keep at edge)
        self.header = PageHeaderWidget("Analytics Dashboard", "View and analyze your data metrics")
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
            'home': self._create_page("Home Page", "Welcome to Desainia MS Tool"),
            'analytics': self._create_page("Analytics", "Analytics Dashboard"),
            'settings': SettingsPage(),  # Use the new SettingsPage
            'files': self._create_page("Files", "File Management")
        }
        
        for name, widget in pages.items():
            self.add_page(name, widget)
    
    def _create_page(self, title, text):
        """Create a placeholder page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel(f"<h1>{title}</h1><p>{text}</p>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return page
    
    def add_page(self, name, widget):
        """Add a new page to the stack"""
        self.pages[name] = self.stack.count()
        self.stack.addWidget(widget)
    
    def show_page(self, name):
        """Switch to specified page"""
        if name in self.pages:
            self.stack.setCurrentIndex(self.pages[name])
            # Update header based on page
            if name == 'home':
                self.header.set_title("Home")
                self.header.set_description("Welcome to Desainia MS Tool")
            elif name == 'analytics':
                self.header.set_title("Analytics Dashboard")
                self.header.set_description("View and analyze your data metrics")
            elif name == 'settings':
                self.header.set_title("Settings")
                self.header.set_description("Configure application settings")
            elif name == 'files':
                self.header.set_title("File Management")
                self.header.set_description("Manage your files and assets")
