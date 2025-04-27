from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGridLayout, 
                            QHBoxLayout, QPushButton, QScrollArea, QApplication)
from PyQt6.QtCore import Qt
import qtawesome as qta
import os
import json

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
            border: 1px solid palette(mid);
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
            background-color: palette(light);
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

# Add tool definitions with IDs
TOOLS = {
    'file_management': {
        'folder_creator': {
            'id': 'tool_folder_creator',
            'title': 'Folder Creator',
            'description': 'Create folders with custom structure',
            'color': "rgba(52, 152, 219, 0.8)"
        },
        'file_renamer': {
            'id': 'tool_file_renamer',
            'title': 'File Renamer',
            'description': 'Batch rename files easily',
            'color': "rgba(46, 204, 113, 0.8)"
        },
        'file_converter': {
            'id': 'tool_file_converter',
            'title': 'File Converter',
            'description': 'Convert between formats',
            'color': "rgba(155, 89, 182, 0.8)"
        },
        'file_organizer': {
            'id': 'tool_file_organizer',
            'title': 'File Organizer',
            'description': 'Sort files automatically',
            'color': "rgba(241, 196, 15, 0.8)"
        }
    },
    'image_processing': {
        'image_converter': {
            'id': 'tool_image_converter',
            'title': 'Image Converter',
            'description': 'Convert between image formats',
            'color': "rgba(231, 76, 60, 0.8)"
        },
        'image_resizer': {
            'id': 'tool_image_resizer',
            'title': 'Image Resizer',
            'description': 'Resize and compress images',
            'color': "rgba(142, 68, 173, 0.8)"
        },
        'image_filter': {
            'id': 'tool_image_filter',
            'title': 'Image Filter',
            'description': 'Apply filters and effects',
            'color': "rgba(230, 126, 34, 0.8)"
        },
        'batch_process': {
            'id': 'tool_batch_process',
            'title': 'Batch Process',
            'description': 'Process multiple images',
            'color': "rgba(41, 128, 185, 0.8)"
        },
        'image_watermark': {
            'id': 'tool_image_watermark',
            'title': 'Image Watermark',
            'description': 'Add text or image watermarks',
            'color': "rgba(39, 174, 96, 0.8)"
        },
        'image_optimizer': {
            'id': 'tool_image_optimizer',
            'title': 'Image Optimizer',
            'description': 'Optimize images for web',
            'color': "rgba(211, 84, 0, 0.8)"
        },
        'image_cropper': {
            'id': 'tool_image_cropper',
            'title': 'Image Cropper',
            'description': 'Crop and adjust images',
            'color': "rgba(22, 160, 133, 0.8)"
        },
        'metadata_editor': {
            'id': 'tool_metadata_editor',
            'title': 'Metadata Editor',
            'description': 'Edit image metadata',
            'color': "rgba(155, 89, 182, 0.8)"
        }
    },
    'video_processing': {
        'video_converter': {
            'id': 'tool_video_converter',
            'title': 'Video Converter',
            'description': 'Convert video formats',
            'color': "rgba(52, 73, 94, 0.8)"
        },
        'video_compressor': {
            'id': 'tool_video_compressor',
            'title': 'Video Compressor',
            'description': 'Compress video files',
            'color': "rgba(192, 57, 43, 0.8)"
        },
        'video_trimmer': {
            'id': 'tool_video_trimmer',
            'title': 'Video Trimmer',
            'description': 'Cut and trim videos',
            'color': "rgba(22, 160, 133, 0.8)"
        },
        'video_merger': {
            'id': 'tool_video_merger',
            'title': 'Video Merger',
            'description': 'Combine multiple videos',
            'color': "rgba(243, 156, 18, 0.8)"
        },
        'audio_extractor': {
            'id': 'tool_audio_extractor',
            'title': 'Audio Extractor',
            'description': 'Extract audio from video',
            'color': "rgba(142, 68, 173, 0.8)"
        },
        'video_resizer': {
            'id': 'tool_video_resizer',
            'title': 'Video Resizer',
            'description': 'Resize video resolution',
            'color': "rgba(39, 174, 96, 0.8)"
        },
        'frame_extractor': {
            'id': 'tool_frame_extractor',
            'title': 'Frame Extractor',
            'description': 'Extract frames from video',
            'color': "rgba(211, 84, 0, 0.8)"
        },
        'subtitle_editor': {
            'id': 'tool_subtitle_editor',
            'title': 'Subtitle Editor',
            'description': 'Add or edit subtitles',
            'color': "rgba(41, 128, 185, 0.8)"
        }
    }
}

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load user preferences using BASE_DIR
        self.app = QApplication.instance()
        self.user_prefs_path = os.path.join(self.app.BASE_DIR.get_path('UserData'), 'user_preferences.json')
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
        
        # Add Favorites section
        favorites_title = QLabel("Favorites")
        favorites_title.setStyleSheet(STYLES['title'])
        favorites_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(favorites_title)
        
        self.favorites_grid = QGridLayout()
        self.favorites_grid.setSpacing(10)
        layout.addLayout(self.favorites_grid)
        
        # Update favorites display
        self.refresh_favorites()
        
        # Change Tools title to File Management
        title = QLabel("File Management")
        title.setStyleSheet(STYLES['title'])
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title)
        
        # Add grid layout with 4 columns directly
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        # Add 4 labeled columns
        for col, tool_key in enumerate(TOOLS['file_management']):
            tool_data = TOOLS['file_management'][tool_key]
            col_widget = self.create_tool_widget(tool_data, grid_layout)
            grid_layout.addWidget(col_widget, 0, col)
            grid_layout.setColumnStretch(col, 1)
        
        layout.addLayout(grid_layout)
        
        # Add Image Processing section
        image_title = QLabel("Image Processing")
        image_title.setStyleSheet(STYLES['title'])
        image_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(image_title)
        
        # Add grid layout for image processing tools
        image_grid = QGridLayout()
        image_grid.setSpacing(10)
        
        row = 0
        col = 0
        for tool_key in TOOLS['image_processing']:
            tool_data = TOOLS['image_processing'][tool_key]
            col_widget = self.create_tool_widget(tool_data, image_grid)
            image_grid.addWidget(col_widget, row, col)
            image_grid.setColumnStretch(col, 1)
            col += 1
            if col == 4:
                col = 0
                row += 1
        
        layout.addLayout(image_grid)
        
        # Add Video Processing section
        video_title = QLabel("Video Processing")
        video_title.setStyleSheet(STYLES['title'])
        video_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(video_title)
        
        # Add grid layout for video processing tools
        video_grid = QGridLayout()
        video_grid.setSpacing(10)
        
        row = 0
        col = 0
        for tool_key in TOOLS['video_processing']:
            tool_data = TOOLS['video_processing'][tool_key]
            col_widget = self.create_tool_widget(tool_data, video_grid)
            video_grid.addWidget(col_widget, row, col)
            video_grid.setColumnStretch(col, 1)
            col += 1
            if col == 4:
                col = 0
                row += 1
        
        layout.addLayout(video_grid)
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
        img_label.setStyleSheet(f"QLabel {{ background-color: {tool_data['color']}; border-radius: 8px; }}")
        
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        # Simple title label without header layout
        title_label = QLabel(tool_data['title'])
        title_label.setStyleSheet(STYLES['tool_title'])
        
        desc_label = QLabel(tool_data['description'])
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
        
        # Rest of the widget
        launch_btn = QPushButton("Open")
        launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        launch_btn.setStyleSheet(STYLES['launch_button'])
        
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
        for idx, tool_id in enumerate(self.user_prefs['favorite_tools']):
            for category in TOOLS.values():
                for tool in category.values():
                    if tool['id'] == tool_id:
                        col = idx % 4
                        row = idx // 4
                        widget = self.create_tool_widget(tool, self.favorites_grid, (row, col))
                        self.favorites_grid.addWidget(widget, row, col)
                        self.favorites_grid.setColumnStretch(col, 1)

    def load_preferences(self):
        with open(self.user_prefs_path, 'r') as f:
            self.user_prefs = json.load(f)

    def save_preferences(self):
        with open(self.user_prefs_path, 'w') as f:
            json.dump(self.user_prefs, f, indent=4)

