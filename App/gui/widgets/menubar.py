from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QAction
import qtawesome as qta

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # File menu
        file_menu = QMenu("File", self)
        new_action = file_menu.addAction(qta.icon('fa5s.file'), "New")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        
        open_action = file_menu.addAction(qta.icon('fa5s.folder-open'), "Open")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        
        save_action = file_menu.addAction(qta.icon('fa5s.save'), "Save")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        
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
        help_menu.addAction(qta.icon('fa5s.info-circle'), "About")
        
        # Add menus to menubar
        self.addMenu(file_menu)
        self.addMenu(edit_menu)
        self.addMenu(view_menu)
        self.addMenu(help_menu)
