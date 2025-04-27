from PyQt6.QtWidgets import QMenuBar, QMenu, QApplication
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QAction, QPalette, QDesktopServices
from .dialogs.about_dialog import AboutDialog
from .dialogs.license_dialog import LicenseDialog
from .dialogs.donate_dialog import DonateDialog
import qtawesome as qta
import platform

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation  # Translation helper
        self.config = self.app.BASE_DIR.config
        self.is_macos = platform.system() == "Darwin"
        self.setup_style()

        # File menu with translations
        file_menu = QMenu(self.tr('menu', 'file', 'title'), self)
        new_action = file_menu.addAction(qta.icon('fa6s.file'), self.tr('menu', 'file', 'new'))
        new_action.setShortcut(QKeySequence.StandardKey.New)
        
        open_action = file_menu.addAction(qta.icon('fa6s.folder-open'), self.tr('menu', 'file', 'open'))
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        
        save_action = file_menu.addAction(qta.icon('fa6s.floppy-disk'), self.tr('menu', 'file', 'save'))
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        
        if not self.is_macos:
            file_menu.addSeparator()
            exit_action = file_menu.addAction(qta.icon('fa6s.power-off'), self.tr('menu', 'file', 'exit'))
            exit_action.setShortcut(QKeySequence.StandardKey.Quit)

        # Edit menu with translations
        edit_menu = QMenu(self.tr('menu', 'edit', 'title'), self)
        undo_action = edit_menu.addAction(qta.icon('fa6s.rotate-left'), self.tr('menu', 'edit', 'undo'))
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        
        redo_action = edit_menu.addAction(qta.icon('fa6s.rotate-right'), self.tr('menu', 'edit', 'redo'))
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        
        edit_menu.addSeparator()
        cut_action = edit_menu.addAction(qta.icon('fa6s.scissors'), self.tr('menu', 'edit', 'cut'))
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        
        copy_action = edit_menu.addAction(qta.icon('fa6s.copy'), self.tr('menu', 'edit', 'copy'))
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        
        paste_action = edit_menu.addAction(qta.icon('fa6s.paste'), self.tr('menu', 'edit', 'paste'))
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        
        if not self.is_macos:
            edit_menu.addSeparator()
            preferences_action = edit_menu.addAction(qta.icon('fa6s.gear'), self.tr('menu', 'edit', 'preferences'))
            preferences_action.setShortcut("Ctrl+,")

        # View menu with translations
        view_menu = QMenu(self.tr('menu', 'view', 'title'), self)
        zoom_in = view_menu.addAction(qta.icon('fa6s.magnifying-glass-plus'), self.tr('menu', 'view', 'zoom_in'))
        zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        
        zoom_out = view_menu.addAction(qta.icon('fa6s.magnifying-glass-minus'), self.tr('menu', 'view', 'zoom_out'))
        zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        
        reset_zoom = view_menu.addAction(qta.icon('fa6s.compress'), self.tr('menu', 'view', 'reset_zoom'))
        reset_zoom.setShortcut("Ctrl+0")

        # Help menu with translations
        help_menu = QMenu(self.tr('menu', 'help', 'title'), self)
        doc_action = help_menu.addAction(qta.icon('fa6s.circle-question'), self.tr('menu', 'help', 'documentation'))
        doc_action.setShortcut("F1")
        doc_action.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl(f"{self.config['repository']['url']}/tree/master/Documentation")))
        
        help_menu.addSeparator()
        join_action = help_menu.addAction(qta.icon('fa6b.whatsapp', color='#25D366'), self.tr('menu', 'help', 'join_group'))
        join_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(self.config['repository']['whatsapp_url'])))
        
        issue_action = help_menu.addAction(qta.icon('fa6s.bug', color='#F05400'), self.tr('menu', 'help', 'report_bug'))
        issue_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(f"{self.config['repository']['url']}/issues")))
        
        help_menu.addSeparator()
        donate_action = help_menu.addAction(qta.icon('fa6s.heart', color='#FF335F'), self.tr('menu', 'help', 'donate'))
        donate_action.triggered.connect(self.show_donate)
        
        license_action = help_menu.addAction(qta.icon('fa6s.file-lines'), self.tr('menu', 'help', 'license'))
        license_action.triggered.connect(self.show_license)
        
        help_menu.addSeparator()
        if not self.is_macos:
            about_action = help_menu.addAction(qta.icon('fa6s.circle-info', color='#0366d6'), self.tr('menu', 'help', 'about'))
            about_action.triggered.connect(self.show_about)

        # Add menus to menubar
        self.addMenu(file_menu)
        self.addMenu(edit_menu)
        self.addMenu(view_menu)
        self.addMenu(help_menu)
    
    def createPopupMenu(self):
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.NoDropShadowWindowHint | Qt.WindowType.FramelessWindowHint)
        return menu

    def setup_style(self):
        """Setup menubar style with professional appearance"""
        palette = self.palette()
        border_color = palette.color(QPalette.ColorRole.Mid).name()
        self.setStyleSheet(f"""
            QMenuBar {{
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
            background-color: rgba(0, 0, 0, 0.05);
            padding: 2px;
            font-size: 13px;
            min-height: 18px;
            }}
            QMenuBar::item {{
            padding: 4px 10px;
            margin: 1px 1px;
            border-radius: 4px;
            }}
            QMenuBar::item:selected {{
            background-color: rgba(102, 102, 102, 0.15);
            }}
            QMenuBar::item:pressed {{
            background-color: rgba(102, 102, 102, 0.25);
            }}
            QMenu {{
            background: palette(window);
            border: 1px solid {border_color};
            border-radius: 4px;
            padding: 5px;
            }}
            QMenu::item {{
            background-color: transparent;
            border-radius: 4px;
            padding: 5px 5px 5px 20px;
            }}
            QMenu::icon {{
            padding-left: 20px;
            }}
            QMenu::item:selected {{
            background-color: rgba(102, 102, 102, 0.15);
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
