from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGraphicsOpacityEffect, QApplication, QPushButton)
from PyQt6.QtCore import Qt, QByteArray, QSize, QRect
from PyQt6.QtGui import QPixmap, QPalette, QColor, QPainter, QPainterPath, QIcon
import qtawesome as qta
from PIL import Image
from io import BytesIO
import json
import os
import webbrowser

class HeaderFrame(QFrame):
    """Base class for header frames"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(127, 127, 127, 0.1);
                border-radius: 10px;
            }
        """)

class AppInfoFrame(HeaderFrame):
    """Frame 1: Application details"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)

        try:
            # Get config using BASE_DIR helper
            app = QApplication.instance()
            config_path = app.BASE_DIR.get_path('App', 'config', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            app_name = QLabel(config['application']['name'])
            app_name.setStyleSheet("font-weight: 600; font-size: 14px; background: transparent; color: rgba(127, 127, 127, 1);")
            
            # Combine version and build info
            version_text = f"v{config['application']['version']}"
            if 'git' in config and 'commit_hash' in config['git']:
                version_text += f" Build: {config['git']['commit_hash']}"
            version_label = QLabel(version_text)
            version_label.setStyleSheet("color: gray; font-size: 10px;")
            
            app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            layout.addWidget(app_name)
            layout.addWidget(version_label)
                
        except Exception as e:
            error_label = QLabel("Error loading app info")
            layout.addWidget(error_label)

class WhatsAppFrame(HeaderFrame):
    """Frame 2: WhatsApp group info"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        app = QApplication.instance()
        tr = app.BASE_DIR.get_translation
        
        # Group name with translation
        group_name = QLabel(tr('header', 'whatsapp', 'title'))
        group_name.setStyleSheet("font-weight: 600; font-size: 14px; background: transparent; color: rgba(127, 127, 127, 1);")
        group_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Join button with translation
        join_button = QPushButton(f" {tr('header', 'whatsapp', 'join')}")
        join_button.setIcon(qta.icon('fa5b.whatsapp', color='#FFFFFF'))
        join_button.setStyleSheet("""
            QPushButton {
                background-color: #128c7e;
                color: #F0F0F0;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
                width: 100px;
            }
            QPushButton:hover {
                background-color: #10645b;
            }
        """)
        join_button.setCursor(Qt.CursorShape.PointingHandCursor)
        join_button.setFixedHeight(25)
        join_button.setFixedWidth(100)
        join_button.clicked.connect(lambda: webbrowser.open('https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3'))
        
        layout.addWidget(group_name)
        layout.addWidget(join_button, alignment=Qt.AlignmentFlag.AlignCenter)

class EmptyFrame(HeaderFrame):
    """Frame 2: Empty placeholder"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

class ImageFrame(HeaderFrame):
    """Frame 3: Background image"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)
        
        app = QApplication.instance()
        image_path = app.BASE_DIR.get_path('App', 'resources', 'public', 'header', 'header.png')
        if os.path.exists(image_path):
            try:
                # Load and process image with PIL first
                with Image.open(image_path) as img:
                    # Convert to RGB/RGBA and remove ICC profile
                    if img.mode in ('RGBA', 'LA'):
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')
                    
                    # Save to buffer without ICC profile
                    buffer = BytesIO()
                    img.save(buffer, format='PNG', icc_profile=None)
                    image_data = buffer.getvalue()
                    
                    # Create QPixmap from processed image data
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(image_data))
                    
                    # Apply rounded corners
                    rounded_pixmap = self.round_corners(pixmap, 10)
                    self.image_label.setPixmap(rounded_pixmap)
            except Exception as e:
                print(f"Error loading image: {str(e)}")
                self.image_label.setText("Error loading image")
        else:
            self.image_label.setText("Header Image")
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.image_label)
  # Ubah ke 1.0 untuk 100% opacity
    def round_corners(self, pixmap, radius):
        """Apply rounded corners to pixmap"""
        if pixmap.isNull():
            return pixmap

        target = QPixmap(pixmap.size())
        target.fill(Qt.GlobalColor.transparent)

        try:
            painter = QPainter(target)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            path = QPainterPath()
            path.addRoundedRect(
                0, 0, 
                pixmap.width(), 
                pixmap.height(), 
                radius, radius
            )

            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
        finally:
            painter.end()

        return target

class DonateFrame(HeaderFrame):
    """Frame for donation button"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        app = QApplication.instance()
        tr = app.BASE_DIR.get_translation
        
        # Title label with translation
        title = QLabel(tr('header', 'donate', 'title'))
        title.setStyleSheet("font-weight: 600; font-size: 14px; background: transparent; color: rgba(127, 127, 127, 1);")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Donate button with translation 
        donate_button = QPushButton(f" {tr('header', 'donate', 'button')}")
        donate_button.setIcon(qta.icon('fa5s.heart', color='#FF335F'))
        donate_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
                width: 100px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        donate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        donate_button.setFixedHeight(25)
        donate_button.setFixedWidth(100)
        donate_button.clicked.connect(self.show_donate_dialog)
        
        layout.addWidget(title)
        layout.addWidget(donate_button, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def show_donate_dialog(self):
        from .dialogs.donate_dialog import DonateDialog
        dialog = DonateDialog(self)
        dialog.exec()

class PageHeaderWidget(QFrame):
    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50)
        
        # Main horizontal layout for frames
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Add frames with adjusted sizes
        app_info = AppInfoFrame()
        whatsapp_frame = WhatsAppFrame()
        donate_frame = DonateFrame()
        image_frame = ImageFrame()
        
        app_info.setFixedWidth(150)
        whatsapp_frame.setFixedWidth(150)
        donate_frame.setFixedWidth(150)
        
        layout.addWidget(app_info)
        layout.addWidget(whatsapp_frame)
        layout.addWidget(donate_frame)
        layout.addWidget(image_frame)
        layout.addStretch()  # Move stretch to end

    # Remove unused methods
    def set_title(self, text): pass
    def set_description(self, text): pass
