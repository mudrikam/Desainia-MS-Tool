from PyQt6.QtWidgets import QMenuBar, QMenu, QApplication
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QAction, QPalette, QDesktopServices
from .dialogs.about_dialog import AboutDialog
from .dialogs.license_dialog import LicenseDialog
from .dialogs.donate_dialog import DonateDialog
import qtawesome as qta
import platform

class MenuBar(QMenuBar):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config  # Store config reference
        self.is_macos = platform.system() == "Darwin"
        self.setup_style()
        
        # Set application details
        QApplication.setApplicationName("Desainia MS Tool")
        QApplication.setOrganizationName("Mudrika")
        QApplication.setApplicationDisplayName("Desainia MS Tool")
        
        # Application menu (macOS)
        if self.is_macos:
            # Create actions with roles first
            about_action = QAction("About Desainia MS Tool", self)
            about_action.setMenuRole(QAction.MenuRole.AboutRole)
            
            preferences_action = QAction("Preferences...", self)
            preferences_action.setMenuRole(QAction.MenuRole.PreferencesRole)
            preferences_action.setShortcut(QKeySequence.StandardKey.Preferences)
            
            quit_action = QAction("Quit Desainia MS Tool", self)
            quit_action.setMenuRole(QAction.MenuRole.QuitRole)
            quit_action.setShortcut(QKeySequence.StandardKey.Quit)
            
            # Add actions to menubar
            self.addAction(about_action)
            self.addAction(preferences_action)
            self.addAction(quit_action)

        # File menu
        file_menu = QMenu("File", self)
        new_action = file_menu.addAction(qta.icon('fa5s.file'), "New")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        
        open_action = file_menu.addAction(qta.icon('fa5s.folder-open'), "Open")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        
        save_action = file_menu.addAction(qta.icon('fa5s.save'), "Save")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        
        # Only add Exit to file menu if not macOS
        if not self.is_macos:
            file_menu.addSeparator()
            exit_action = file_menu.addAction(qta.icon('fa5s.power-off'), "Exit")
            exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        
        # Edit menu
        edit_menu = QMenu("Edit", self)
        undo_action = edit_menu.addAction(qta.icon('fa5s.undo'), "Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        
        redo_action = edit_menu.addAction(qta.icon('fa5s.redo'), "Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        
        edit_menu.addSeparator()
        cut_action = edit_menu.addAction(qta.icon('fa5s.cut'), "Cut")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        
        copy_action = edit_menu.addAction(qta.icon('fa5s.copy'), "Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        
        paste_action = edit_menu.addAction(qta.icon('fa5s.paste'), "Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        
        # Add preferences to Edit menu if not macOS
        if not self.is_macos:
            edit_menu.addSeparator()
            preferences_action = edit_menu.addAction(qta.icon('fa5s.cog'), "Preferences")
            preferences_action.setShortcut("Ctrl+,")
        
        # View menu
        view_menu = QMenu("View", self)
        zoom_in = view_menu.addAction(qta.icon('fa5s.search-plus'), "Zoom In")
        zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        
        zoom_out = view_menu.addAction(qta.icon('fa5s.search-minus'), "Zoom Out")
        zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        
        reset_zoom = view_menu.addAction(qta.icon('fa5s.compress-arrows-alt'), "Reset Zoom")
        reset_zoom.setShortcut("Ctrl+0")
        
        # Help menu
        help_menu = QMenu("Help", self)
        help_menu.addAction(qta.icon('fa5s.question-circle'), "Documentation").setShortcut("F1")
        
        help_menu.addSeparator()
        join_action = help_menu.addAction(qta.icon('fa5b.whatsapp', color='#25D366'), "Join Our Group")
        join_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3")))
        
        issue_action = help_menu.addAction(qta.icon('fa5s.bug',color='#F05400'), "Found a Bug?")
        issue_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/mudrikam/Desainia-MS-Tool/issues")))
        
        help_menu.addSeparator()
        donate_action = help_menu.addAction(qta.icon('fa5s.heart', color='#FF335F'), "Donate")
        donate_action.triggered.connect(self.show_donate)
        
        license_action = help_menu.addAction(qta.icon('fa5s.file-contract'), "License")
        license_action.triggered.connect(self.show_license)
        
        help_menu.addSeparator()
        if not self.is_macos:
            about_action = help_menu.addAction(qta.icon('fa5s.info-circle', color='#0366d6'), "About")
            about_action.triggered.connect(self.show_about)
        
        # Add menus to menubar
        self.addMenu(file_menu)
        self.addMenu(edit_menu)
        self.addMenu(view_menu)
        self.addMenu(help_menu)
    
    def setup_style(self):
        """Setup menubar style with system border color"""
        palette = self.palette()
        border_color = palette.color(QPalette.ColorRole.Mid).name()
        self.setStyleSheet(f"""
            QMenuBar {{
                border-bottom: 1px solid {border_color};
                background: transparent;
            }}
        """)

    def show_about(self):
        """Show about dialog"""
        app = QApplication.instance()
        config_path = app.BASE_DIR.get_path('App', 'config', 'config.json')
        with open(config_path, 'r') as f:
            import json
            config = json.load(f)
        dialog = AboutDialog(config, self)
        dialog.exec()

    def show_license(self):
        """Show license dialog"""
        dialog = LicenseDialog(self)
        dialog.exec()

    def show_donate(self):
        """Show donate dialog"""
        dialog = DonateDialog(self)
        dialog.exec()
