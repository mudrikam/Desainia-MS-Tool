import json, os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen, QIcon
from .widgets.sidebar import SideBar
from .widgets.menubar import MenuBar
from .widgets.statusbar import StatusBar
from .widgets.content import ContentWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_ui()
        self._center_window()
    
    def _init_window(self):
        """Initialize window properties"""
        app = QApplication.instance()
        
        # Load config
        config_path = app.BASE_DIR.get_path('App', 'config', 'config.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Set window properties
        self.setWindowTitle(self.config['window']['title'])
        self.resize(self.config['window']['width'], self.config['window']['height'])
        if self.config['window']['min_width'] and self.config['window']['min_height']:
            self.setMinimumSize(self.config['window']['min_width'], 
                              self.config['window']['min_height'])
        
        # Set window icon
        try:
            icon_path = app.BASE_DIR.get_path(self.config['window']['icon'])
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    app.setWindowIcon(icon)
        except Exception as e:
            print(f"Error setting icon: {str(e)}")
    
    def _init_ui(self):
        """Initialize UI components"""
        # Create menubar
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)
        
        # Create statusbar
        self.statusbar = StatusBar(self.config, self)
        self.setStatusBar(self.statusbar)
        
        # Create main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_content()  # Only call _setup_content()
    
    def _setup_content(self):
        """Setup main content area"""
        # Create sidebar and content
        self.sidebar = SideBar(self)
        self.content = ContentWidget(self)
        
        # Connect sidebar signals
        self.sidebar.home_clicked.connect(lambda: self.content.show_page('home'))
        self.sidebar.settings_clicked.connect(lambda: self.content.show_page('settings'))
        self.sidebar.account_clicked.connect(lambda: self.content.show_page('user'))
        
        # Connect content page_changed signal to sidebar handler
        self.content.page_changed.connect(self.sidebar.handle_page_changed)
        
        # Add to layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content)
        
        # Show user page as default instead of home page
        self.content.show_page('user')
        # Update sidebar to highlight the account button
        self.content.page_changed.emit('user')
    
    def _center_window(self):
        """Center window on screen"""
        if not self.config['window'].get('start_maximized', False):
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            self.showMaximized()
