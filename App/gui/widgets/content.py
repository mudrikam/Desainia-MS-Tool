from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from .pages.settings_page import SettingsPage
from .pages.home_page import HomePage
from .header import PageHeaderWidget

class ContentWidget(QWidget):
    # Add a signal to notify when the page changes
    page_changed = pyqtSignal(str)
    
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
        
        # Initialize pages
        self.pages = {}
        self._init_pages()
    
    def _init_pages(self):
        """Initialize default pages"""
        # Import pages
        from .pages.home_page import HomePage
        from .pages.settings_page import SettingsPage
        from .pages.user.user import UserPage
        
        # Create pages
        self.add_page('home', HomePage(self))
        self.add_page('settings', SettingsPage(self))
        self.add_page('user', UserPage(self))  # Add the user page
        
        # Set initial page
        self.show_page('home')

    def add_page(self, name, page_widget):
        """Add a page to the stack"""
        self.pages[name] = page_widget
        self.stack.addWidget(page_widget)
        
    def remove_page(self, name):
        """Remove a page from the stack"""
        if name in self.pages:
            self.stack.removeWidget(self.pages[name])
            del self.pages[name]
    
    def show_page(self, name):
        """Show a specific page by name"""
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])
            self.page_changed.emit(name)  # Emit signal to update sidebar highlighting
