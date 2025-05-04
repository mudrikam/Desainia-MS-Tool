from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGridLayout, 
                            QHBoxLayout, QPushButton, QScrollArea, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import qtawesome as qta
import os
import json
import importlib.util
import sys

# Centralized styles
STYLES = {
    'title': """
        font-size: 18px;
        font-weight: 600;
        color: palette(windowText);
    """,
    
    'tool_widget': """
        QWidget#tool_container { 
            background-color: palette(light);
            border-radius: 10px;
        }
        QWidget#tool_container:hover {
            background-color: palette(light);
            border-radius: 10px;
            border: 1px solid rgba(127, 127, 127, 0.5);
        }
    """,
    
    'tool_title': """
        font-weight: 600;
        font-size: 14px;
        color: palette(text);
        background: transparent;
    """,
    
    'tool_description': """
        font-size: 11px;
        background: transparent;
        color: rgba(127, 127, 127, 1);
    """,
    
    'launch_button': """
        QPushButton {
            background-color: palette(button);
            border: none;
            border-radius: 5px;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #0366d6;
            color: #FFFFFF;
        }
    """,
    
    'star_button': """
        QPushButton {
            background: transparent;
            border: none;
            padding: 0;
            margin: 0;
        }
    """,

    'lorem_text': """
        color: palette(text);
        font-size: 13px;
        padding: 20px 0;
    """
}

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load user preferences using BASE_DIR
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation  # Translation helper
        self.user_prefs_path = os.path.join(self.app.BASE_DIR.get_path('UserData'), 'user_preferences.json')
        
        # Load tools dictionary from JSON file
        tools_dict_path = self.app.BASE_DIR.get_path('App', 'config', '_home_page_dictionary.json')
        with open(tools_dict_path, 'r') as f:
            self.TOOLS = json.load(f)
            
        self.load_preferences()
        
        # Ensure favorite_tools exists
        if 'favorite_tools' not in self.user_prefs:
            self.user_prefs['favorite_tools'] = []
            self.save_preferences()
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Create content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        
        # Add Favorites section with translation
        favorites_title = QLabel(self.tr('page', 'home', 'favorites'))
        favorites_title.setStyleSheet(STYLES['title'])
        favorites_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(favorites_title)
        
        self.favorites_grid = QGridLayout()
        self.favorites_grid.setSpacing(10)
        layout.addLayout(self.favorites_grid)
        
        # Update favorites display
        self.refresh_favorites()
        
        # Dynamically render all tool categories
        for category_key, category_tools in self.TOOLS.items():
            # Check if there are any enabled tools in this category
            has_enabled_tools = any(t.get('enabled', False) for t in category_tools.values())
            if not has_enabled_tools:
                continue
                
            # Add category title with translation
            title = QLabel(self.tr('page', 'home', category_key))
            title.setStyleSheet(STYLES['title'])
            title.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(title)
            
            # Create grid layout for the category
            grid_layout = QGridLayout()
            grid_layout.setSpacing(10)
            
            # Add tools to grid
            row = 0
            col = 0
            for tool_key, tool_data in category_tools.items():
                # Skip disabled tools
                if not tool_data.get('enabled', False):
                    continue
                    
                col_widget = self.create_tool_widget(tool_data, grid_layout)
                grid_layout.addWidget(col_widget, row, col)
                grid_layout.setColumnStretch(col, 1)
                
                col += 1
                if col == 4:  # 4 columns per row
                    col = 0
                    row += 1
            
            layout.addLayout(grid_layout)
        
        layout.addStretch()
        
        # Add extra space at bottom to ensure scrolling
        spacer = QWidget()
        spacer.setMinimumHeight(20)  # minimum bottom padding
        layout.addWidget(spacer)
        
        # Set content widget to scroll area
        scroll.setWidget(content)
        
        # Add scroll area to main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_tool_widget(self, tool_data, parent_layout, position=None):
        col_widget = QWidget()
        col_widget.setObjectName("tool_container")  # Add object name for specific styling
        col_widget.setMinimumWidth(150)
        col_layout = QVBoxLayout(col_widget)
        col_layout.setContentsMargins(10, 10, 10, 10)
        col_layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        img_label = QLabel()
        img_label.setFixedSize(50, 50)
        
        # Try to load the icon from file
        icon_path = None
        if 'icon' in tool_data:
            icon_name = tool_data['icon']
            icon_path = self.app.BASE_DIR.get_path('App', 'resources', 'public', 'img', 'icons', 'tools', icon_name)
            
            # Check if the icon file exists
            if not os.path.exists(icon_path):
                # Try with .svg extension if the file doesn't exist
                svg_path = os.path.splitext(icon_path)[0] + '.svg'
                if os.path.exists(svg_path):
                    icon_path = svg_path
                else:
                    # Fall back to default.svg
                    icon_path = self.app.BASE_DIR.get_path('App', 'resources', 'public', 'img', 'icons', 'tools', 'default.svg')
        else:
            # Fall back to default.svg if no icon is specified
            icon_path = self.app.BASE_DIR.get_path('App', 'resources', 'public', 'img', 'icons', 'tools', 'default.svg')
        
        # Load the image if the icon path exists
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            img_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            # Use colored background if image loading fails
            img_label.setStyleSheet(f"QLabel {{ background-color: {tool_data['color']}; border-radius: 8px; }}")
        
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        # Manual lookup from translation file instead of using tr function
        try:
            # Access translation based on current language
            language = self.app.BASE_DIR.config["application"]["language"]
            
            tool_name = tool_data['id'].replace('tool_', '')
            
            # Load translation.json directly
            translation_path = self.app.BASE_DIR.get_path('App', 'config', 'translation.json')
            with open(translation_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Fetch the title and description from the translation file
            title_text = translations.get(language, {}).get('tools', {}).get(tool_name, {}).get('title', tool_data.get('title', tool_data['id']))
            desc_text = translations.get(language, {}).get('tools', {}).get(tool_name, {}).get('description', tool_data.get('description', ''))
        except Exception:
            title_text = tool_data.get('title', tool_data['id'])
            desc_text = tool_data.get('description', '')
        
        # Simple title label without header layout
        title_label = QLabel(title_text)
        title_label.setStyleSheet(STYLES['tool_title'])
        
        desc_label = QLabel(desc_text)
        desc_label.setStyleSheet(STYLES['tool_description'])
        desc_label.setWordWrap(True)
        
        title_container.addWidget(title_label)
        title_container.addWidget(desc_label)
        
        # Star button
        star_btn = QPushButton()
        star_btn.setObjectName("star_button")
        star_btn.setProperty('tool_id', tool_data['id'])
        star_btn.setFixedSize(24, 24)
        star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        star_btn.setStyleSheet(STYLES['star_button'])
        is_favorite = tool_data['id'] in self.user_prefs['favorite_tools']
        star_icon = qta.icon('fa6s.star', 
                           color='#f39c12' if is_favorite else '#757575',
                           color_disabled='#757575')
        star_btn.setIcon(star_icon)
        star_btn.setProperty('favorite', is_favorite)
        star_btn.clicked.connect(lambda checked, tid=tool_data['id']: self.toggle_favorite(tid))
        
        # Main header layout order: image, title container, star
        header_layout.addWidget(img_label)
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(star_btn)
        
        # Launch button with connection to the tool's function if available
        launch_btn = QPushButton("Open")
        launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        launch_btn.setStyleSheet(STYLES['launch_button'])
        
        # Connect launch button to the generic tool handler
        if 'function' in tool_data:
            launch_btn.clicked.connect(lambda checked, tid=tool_data['id']: self._launch_tool(tid))
        
        col_layout.addLayout(header_layout)
        col_layout.addWidget(launch_btn)
        
        col_widget.setStyleSheet(STYLES['tool_widget'])
        return col_widget

    def toggle_favorite(self, tool_id):
        if tool_id in self.user_prefs['favorite_tools']:
            self.user_prefs['favorite_tools'].remove(tool_id)
        else:
            self.user_prefs['favorite_tools'].append(tool_id)
        
        self.save_preferences()
        self.refresh_favorites()
        
        # Update the star button in the current view
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QScrollArea):
                self._update_star_buttons(widget.widget())

    def _update_star_buttons(self, widget):
        # Helper method to update star buttons
        tool_widgets = widget.findChildren(QWidget)
        for tool_widget in tool_widgets:
            star_btn = tool_widget.findChild(QPushButton, "star_button")
            if star_btn and star_btn.property('tool_id'):
                tool_id = star_btn.property('tool_id')
                is_favorite = tool_id in self.user_prefs['favorite_tools']
                star_icon = qta.icon('fa6s.star', 
                    color='#f39c12' if is_favorite else '#757575',
                    color_disabled='#757575')
                star_btn.setIcon(star_icon)

    def refresh_favorites(self):
        # Clear existing favorites
        for i in reversed(range(self.favorites_grid.count())): 
            self.favorites_grid.itemAt(i).widget().setParent(None)
        
        # Add favorite tools
        row, col = 0, 0
        for tool_id in self.user_prefs['favorite_tools']:
            # Find the tool in all categories
            tool = None
            for category in self.TOOLS.values():
                for t in category.values():
                    if t['id'] == tool_id and t.get('enabled', False):
                        tool = t
                        break
                if tool:
                    break
            
            if tool:
                widget = self.create_tool_widget(tool, self.favorites_grid, (row, col))
                self.favorites_grid.addWidget(widget, row, col)
                self.favorites_grid.setColumnStretch(col, 1)
                
                col += 1
                if col == 4:  # 4 columns per row
                    col = 0
                    row += 1

    def load_preferences(self):
        with open(self.user_prefs_path, 'r') as f:
            self.user_prefs = json.load(f)

    def save_preferences(self):
        with open(self.user_prefs_path, 'w') as f:
            json.dump(self.user_prefs, f, indent=4)
    
    def _launch_tool(self, tool_id):
        """Launch tool by dynamically importing and showing the tool module"""
        try:
            # Get tool category and name
            for category in self.TOOLS.values():
                for tool_data in category.values():
                    if tool_data['id'] == tool_id:
                        # Extract tool name from ID (remove 'tool_' prefix)
                        tool_name = tool_id.replace('tool_', '')
                        
                        # Construct path to tool module
                        tool_path = self.app.BASE_DIR.get_path('App', 'gui', 'widgets', 'pages', 'tools', tool_name, f"{tool_name}.py")
                        
                        if os.path.exists(tool_path):
                            # Import module dynamically
                            spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[tool_name] = module
                            spec.loader.exec_module(module)
                            
                            # Get the main tool class (assuming it follows naming convention)
                            tool_class_name = ''.join(word.capitalize() for word in tool_name.split('_')) + 'Tool'
                            if hasattr(module, tool_class_name):
                                tool_class = getattr(module, tool_class_name)
                                # Instantiate and show the tool
                                tool_instance = tool_class(self)
                                
                                # Get the main window content widget to show the tool
                                main_window = self.window()
                                if hasattr(main_window, 'content'):
                                    content_widget = main_window.content
                                    # Add the page if it doesn't exist
                                    if tool_id not in content_widget.pages:
                                        content_widget.add_page(tool_id, tool_instance)
                                    content_widget.show_page(tool_id)
                                    return
                        break
            
            print(f"Could not find tool module for {tool_id}")
        except Exception as e:
            print(f"Error launching tool {tool_id}: {str(e)}")


