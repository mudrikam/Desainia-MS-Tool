from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, 
    QApplication, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath, QBrush
import qtawesome as qta
import datetime
import os

# Import the database module for user data
from App.core.database import UserDashboardDB
from App.core.user._user_auth import UserAuth
from App.core.user._user_session_handler import session
from App.core.database._db_user_attendance import attendance_db

class CircularImageLabel(QLabel):
    """A custom QLabel that displays images in a circular shape"""
    
    def __init__(self, parent=None, border_width=3, border_color="transparent"):
        super().__init__(parent)
        self.setMinimumSize(100, 100)
        self.setMaximumSize(100, 100)
        self._pixmap = None
        self.border_width = border_width
        self.border_color = border_color
        
    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update_image()
        
    def set_border_color(self, color):
        """Set the border color and redraw the image"""
        self.border_color = color
        self.update_image()
        
    def update_image(self):
        """Update the circular image with current border settings"""
        if self._pixmap:
            super().setPixmap(self._get_circular_pixmap())
        
    def _get_circular_pixmap(self):
        if self._pixmap is None:
            return QPixmap()
            
        # Create empty pixmap with desired dimensions
        target = QPixmap(self.width(), self.height())
        target.fill(Qt.GlobalColor.transparent)
        
        # Create painter for the target
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Create circular path for border
        border_path = QPainterPath()
        border_path.addEllipse(0, 0, self.width(), self.height())
        
        # Draw border if border color is not transparent
        if self.border_color != "transparent":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.border_color))
            painter.drawPath(border_path)
        
        # Create circular path for image (smaller to account for border)
        image_path = QPainterPath()
        image_rect = self.width() - (self.border_width * 2)
        image_path.addEllipse(
            self.border_width, 
            self.border_width, 
            image_rect, 
            image_rect
        )
        
        painter.setClipPath(image_path)
        
        # Scale the pixmap to fill the circular area
        scaled_pixmap = self._pixmap.scaled(image_rect, image_rect,
                                      Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                      Qt.TransformationMode.SmoothTransformation)
        
        # Calculate position to center the pixmap
        x = self.border_width
        y = self.border_width
        
        # Draw the pixmap
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        return target

class UserSidebar(QFrame):
    """Left profile sidebar widget for the user dashboard."""
    
    # Signal for logout
    logout_requested = pyqtSignal()
    
    # Centralized styles
    STYLES = {
        # Common colors
        "colors": {
            "danger": "#dc3545",
            "danger_hover": "rgba(220, 53, 69, 0.1)",
            "danger_pressed": "rgba(220, 53, 69, 0.2)",
        },
        
        # Sidebar container
        "sidebar": """
            #leftPanel {
                background-color: palette(alternateBase);
                border: none;
                border-radius: 12px;
            }
        """,
        
        # Text styles
        "fullname": """
            font-size: 20px;
            font-weight: 600;
            color: palette(text);
            margin-top: 15px;
            margin-bottom: 0px;
        """,
        
        "username_pill": """
            font-size: 12px;
            color: palette(highlight);
            font-weight: 500;
            background-color: palette(alternateBase);
            border: 1px solid palette(highlight);
            border-radius: 10px;
            padding: 2px 10px;
        """,
        
        "info_text": """
            font-size: 11px;
            color: palette(text);
        """,
        
        # Logout button
        "logout_button": """
            QPushButton {
                background-color: transparent;
                color: #dc3545;
                border: 1px solid #dc3545;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: 500;
                outline: none;
                text-align: center;
            }
            QPushButton:focus {
                outline: none;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.2);
            }
        """
    }
    
    def __init__(self, parent=None, username="User"):
        super().__init__(parent)
        self.username = username
        self.setObjectName("leftPanel")
        self.setFixedWidth(220)  # Fixed width for left panel
        self.setStyleSheet(self.STYLES["sidebar"])
        
        # Get app instance 
        self.app = QApplication.instance()
        
        # Initialize database handler
        self.db_handler = UserDashboardDB(self.app)
        
        # Get user data from database
        self.user_data = self.db_handler.get_user_data(username)
        self.fullname = self.user_data.get('fullname', username) if self.user_data else username
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components of the sidebar"""
        # Left panel layout
        left_layout = QVBoxLayout(self)
        left_layout.setContentsMargins(15, 25, 15, 20)
        left_layout.setSpacing(5)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Profile section
        profile_section = QVBoxLayout()
        profile_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_section.setSpacing(5)
        
        # User avatar
        self.profile_image = CircularImageLabel()
        self.profile_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Check if user has a profile image
        profile_image_path = None
        if self.user_data and self.user_data.get('profile_image'):
            # Convert dari path relatif ke path absolut
            relative_path = self.user_data.get('profile_image')
            profile_image_path = self.db_handler.get_profile_image_path(relative_path)
            
        if profile_image_path and os.path.exists(profile_image_path):
            # User has a profile image, load it
            pixmap = QPixmap(profile_image_path)
            self.profile_image.setPixmap(pixmap)
        else:
            # Create a colored circle with initials
            # Create empty pixmap
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Setup painter to draw on pixmap
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Get user initials
            initials = ""
            if self.fullname:
                for part in self.fullname.split():
                    if part:
                        initials += part[0].upper()
                        if len(initials) >= 2:
                            break
            
            # If no initials available, use first letter of username
            if not initials and self.username:
                initials = self.username[0].upper()
            
            # Generate a color based on the username
            color_value = 0
            for c in self.username:
                color_value += ord(c)
            
            hue = (color_value % 360) / 360.0  # Normalize to [0-1]
            color = QColor.fromHsvF(hue, 0.5, 0.9)  # Pastel shade
            
            # Draw colored circle
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, 100, 100)
            
            # Draw text
            painter.setPen(Qt.GlobalColor.white)
            font = painter.font()
            font.setPointSize(36)
            font.setBold(True)
            painter.setFont(font)
            
            # Center text
            rect = pixmap.rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)
            painter.end()
            
            # Set pixmap to label
            self.profile_image.setPixmap(pixmap)
        
        # Fullname label (larger)
        self.fullname_label = QLabel(self.fullname)
        self.fullname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fullname_label.setWordWrap(True)
        self.fullname_label.setStyleSheet(self.STYLES["fullname"])
        
        # Username dalam pill
        username_pill = QLabel(f"@{self.username}")
        username_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_pill.setStyleSheet(self.STYLES["username_pill"])
        
        # Format username pill to be more compact
        username_container = QWidget()
        username_container_layout = QHBoxLayout(username_container)
        username_container_layout.setContentsMargins(0, 5, 0, 5)
        username_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_container_layout.addWidget(username_pill)
        
        # Last login info
        last_login_str = "Never"
        if self.user_data and self.user_data.get('last_login'):
            try:
                # Try to parse the last_login timestamp
                last_login = datetime.datetime.fromisoformat(str(self.user_data.get('last_login')))
                last_login_str = last_login.strftime("%d %b %Y, %H:%M")
            except:
                last_login_str = str(self.user_data.get('last_login', 'Never'))
        
        last_login_container = QWidget()
        last_login_layout = QHBoxLayout(last_login_container)
        last_login_layout.setContentsMargins(0, 5, 0, 5)
        
        last_login_icon = QLabel()
        last_login_icon.setPixmap(qta.icon("fa6s.clock", color=QApplication.palette().mid().color().name()).pixmap(12, 12))
        
        last_login_text = QLabel(f"Last login: {last_login_str}")
        last_login_text.setStyleSheet(self.STYLES["info_text"])
        
        last_login_layout.addWidget(last_login_icon)
        last_login_layout.addWidget(last_login_text)
        last_login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Department info (if available)
        department_container = None
        if self.user_data and self.user_data.get('department'):
            department_container = QWidget()
            department_layout = QHBoxLayout(department_container)
            department_layout.setContentsMargins(0, 5, 0, 5)
            
            department_icon = QLabel()
            department_icon.setPixmap(qta.icon("fa6s.building", color=QApplication.palette().mid().color().name()).pixmap(12, 12))
            
            department_text = QLabel(self.user_data.get('department'))
            department_text.setStyleSheet(self.STYLES["info_text"])
            
            department_layout.addWidget(department_icon)
            department_layout.addWidget(department_text)
            department_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Start date info (if available)
        start_date_container = None
        if self.user_data and self.user_data.get('start_date'):
            start_date_container = QWidget()
            start_date_layout = QHBoxLayout(start_date_container)
            start_date_layout.setContentsMargins(0, 5, 0, 5)
            
            start_date_icon = QLabel()
            start_date_icon.setPixmap(qta.icon("fa6s.calendar-day", color=QApplication.palette().mid().color().name()).pixmap(12, 12))
            
            # Format the date nicely
            start_date_str = self.user_data.get('start_date')
            try:
                date_obj = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %b %Y")
            except:
                formatted_date = start_date_str
                
            start_date_text = QLabel(f"Started: {formatted_date}")
            start_date_text.setStyleSheet(self.STYLES["info_text"])
            
            start_date_layout.addWidget(start_date_icon)
            start_date_layout.addWidget(start_date_text)
            start_date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # WhatsApp number info (if available)
        whatsapp_container = None
        if self.user_data and self.user_data.get('phone_number'):
            whatsapp_container = QWidget()
            whatsapp_layout = QHBoxLayout(whatsapp_container)
            whatsapp_layout.setContentsMargins(0, 5, 0, 5)
            
            whatsapp_icon = QLabel()
            whatsapp_icon.setPixmap(qta.icon("fa6b.whatsapp", color=QApplication.palette().mid().color().name()).pixmap(12, 12))
            
            whatsapp_text = QLabel(self.user_data.get('phone_number'))
            whatsapp_text.setStyleSheet(self.STYLES["info_text"])
            
            whatsapp_layout.addWidget(whatsapp_icon)
            whatsapp_layout.addWidget(whatsapp_text)
            whatsapp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Email info (if available)
        email_container = None
        if self.user_data and self.user_data.get('email'):
            email_container = QWidget()
            email_layout = QHBoxLayout(email_container)
            email_layout.setContentsMargins(0, 5, 0, 5)
            
            email_icon = QLabel()
            email_icon.setPixmap(qta.icon("fa6s.envelope", color=QApplication.palette().mid().color().name()).pixmap(12, 12))
            
            email_text = QLabel(self.user_data.get('email'))
            email_text.setStyleSheet(self.STYLES["info_text"])
            
            email_layout.addWidget(email_icon)
            email_layout.addWidget(email_text)
            email_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add profile elements to profile section
        profile_section.addWidget(self.profile_image, 0, Qt.AlignmentFlag.AlignCenter)
        profile_section.addWidget(self.fullname_label)
        profile_section.addWidget(username_container)
        profile_section.addWidget(last_login_container)
        if department_container:
            profile_section.addWidget(department_container)
        if start_date_container:
            profile_section.addWidget(start_date_container)
        if whatsapp_container:
            profile_section.addWidget(whatsapp_container)
        if email_container:
            profile_section.addWidget(email_container)
        
        # Add profile section to left layout
        left_layout.addLayout(profile_section)
        
        # Add spacer to push logout button to bottom
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Logout button at bottom with improved styling
        logout_btn = QPushButton("Logout")
        logout_icon = qta.icon("fa6s.right-from-bracket", color=self.STYLES["colors"]["danger"])
        logout_btn.setIcon(logout_icon)
        logout_btn.setIconSize(logout_btn.iconSize() * 0.8)
        logout_btn.setStyleSheet(self.STYLES["logout_button"])
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self._on_logout)
        
        # Add logout button to left layout
        left_layout.addWidget(logout_btn)
    
    def _on_logout(self):
        """Handle logout button click"""
        # Import auth helper and logout
        auth = UserAuth(self.app)
        
        # Get current user before logout
        current_user = auth.get_current_user()
        if current_user:
            print(f"Logging out user: {current_user.get('username', 'unknown')}")
        
        # Ensure remember_login is disabled
        auth.update_settings(remember_login=False)
        
        # Perform the logout
        auth.logout()
        
        # Emit signal to notify parent
        self.logout_requested.emit()
    
    def showEvent(self, event):
        """Called when the widget is shown."""
        # Check attendance status when sidebar is shown
        self.check_attendance_status()
        super().showEvent(event)
    
    def check_attendance_status(self):
        """Check if the user is currently checked in and update the profile image border."""
        if not session.is_logged_in():
            return
            
        try:
            # Get current user ID from session
            user_id = session.get_user_id()
            if not user_id:
                return
                
            # Get any unclosed attendance record regardless of date
            # This ensures consistency with the attendance page
            unclosed_record = attendance_db.get_unclosed_attendance_record(user_id)
            
            # If any unclosed record exists, user is considered checked in
            if unclosed_record and unclosed_record.get('check_in_time') and not unclosed_record.get('check_out_time'):
                # Update profile photo border to green to indicate checked in
                self.profile_image.set_border_color("#4CAF50")  # Green border for checked in
            else:
                # Reset profile photo border to transparent for checked out
                self.profile_image.set_border_color("transparent")
                
        except Exception as e:
            print(f"Failed to check attendance status in sidebar: {e}")
            
    def update_username(self, username):
        """Update the displayed username with fresh data from database"""
        self.username = username
        
        # Get user data from database with no_cache=True to get fresh data
        self.db_handler = UserDashboardDB(self.app)
        self.user_data = self.db_handler.get_user_data(username, no_cache=True)
        self.fullname = self.user_data.get('fullname', username) if self.user_data else username
        
        # Update labels
        self.fullname_label.setText(self.fullname)
        
        # Update username pill
        for child in self.findChildren(QLabel):
            if child.text().startswith('@'):
                child.setText(f"@{self.username}")
        
        # Update profile image with fresh data
        profile_image_path = None
        if self.user_data and self.user_data.get('profile_image'):
            # Convert dari path relatif ke path absolut
            relative_path = self.user_data.get('profile_image')
            profile_image_path = self.db_handler.get_profile_image_path(relative_path)
        
        if profile_image_path and os.path.exists(profile_image_path):
            # User has a profile image, load it
            pixmap = QPixmap(profile_image_path)
            self.profile_image.setPixmap(pixmap)
        else:
            # No profile image, use default icon
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Get user initials
            initials = ""
            if self.fullname:
                for part in self.fullname.split():
                    if part:
                        initials += part[0].upper()
                        if len(initials) >= 2:
                            break
            
            # If no initials available, use first letter of username
            if not initials and self.username:
                initials = self.username[0].upper()
            
            # Generate color based on username
            color_value = 0
            for c in self.username:
                color_value += ord(c)
            
            hue = (color_value % 360) / 360.0
            color = QColor.fromHsvF(hue, 0.5, 0.9)
            
            # Draw colored circle
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, 100, 100)
            
            # Draw text
            painter.setPen(Qt.GlobalColor.white)
            font = painter.font()
            font.setPointSize(36)
            font.setBold(True)
            painter.setFont(font)
            
            rect = pixmap.rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)
            painter.end()
            
            self.profile_image.setPixmap(pixmap)
            
        # Check attendance status after updating profile image
        self.check_attendance_status()