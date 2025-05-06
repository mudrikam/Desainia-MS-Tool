from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QSizePolicy, QScrollArea, QGroupBox, QFormLayout, QApplication
)
from PyQt6.QtCore import Qt, QDate

# Import the database module for user data
from App.core.database import UserDashboardDB

class UserProfileWidget(QWidget):
    """User profile widget for the dashboard."""
    
    def __init__(self, parent=None, username="User", app_instance=None):
        super().__init__(parent)
        self.username = username
        self.app = app_instance
        
        # Initialize database handler
        self.db_handler = UserDashboardDB(self.app)
        
        # Get user data from database with full profile
        self.user_data = self.db_handler.get_user_data(username, no_cache=True, include_profile=True)
        self.fullname = self.user_data.get('fullname', username) if self.user_data else username
        
        # Set up the UI
        self._setup_ui()
        
        # Load profile data
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget to hold all profile elements
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        
        # Create header section
        header_section = QHBoxLayout()
        
        # Profile image (will be loaded dynamically in refresh_data)
        self.profile_image_label = QLabel()
        self.profile_image_label.setFixedSize(100, 100)
        self.profile_image_label.setStyleSheet("border-radius: 50px;")
        
        # User info next to profile image
        user_info_layout = QVBoxLayout()
        
        # Full name in large bold text
        self.name_label = QLabel(self.fullname)
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # Username with @ prefix
        self.username_label = QLabel(f"@{self.username}")
        self.username_label.setStyleSheet("font-size: 16px; color: palette(mid);")
        
        # Add to user info layout
        user_info_layout.addWidget(self.name_label)
        user_info_layout.addWidget(self.username_label)
        user_info_layout.addStretch()
        
        # Add to header section
        header_section.addWidget(self.profile_image_label)
        header_section.addLayout(user_info_layout)
        header_section.addStretch(1)
        
        # Add header to content layout
        content_layout.addLayout(header_section)
        
        # ============ PERSONAL INFORMATION ============
        self.personal_section = QGroupBox("Personal Information")
        self.personal_section.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.personal_layout = QFormLayout(self.personal_section)
        self.personal_layout.setVerticalSpacing(12)
        self.personal_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Add personal section to content layout (initially empty, will be populated in refresh_data)
        content_layout.addWidget(self.personal_section)
        
        # ============ EMPLOYMENT INFORMATION ============
        self.employment_section = QGroupBox("Employment Information")
        self.employment_section.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.employment_layout = QFormLayout(self.employment_section)
        self.employment_layout.setVerticalSpacing(12)
        self.employment_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Add employment section to content layout (initially empty, will be populated in refresh_data)
        content_layout.addWidget(self.employment_section)
        
        # Add spacer at the bottom
        content_layout.addStretch()
        
        # Hide empty sections initially
        self.personal_section.setVisible(False)
        self.employment_section.setVisible(False)
        
        # Store section references for later
        self.content_layout = content_layout
    
    def refresh_data(self):
        """Refresh user data from database and update UI"""
        # Get fresh user data from database
        self.user_data = self.db_handler.get_user_data(self.username, no_cache=True, include_profile=True)
        self.fullname = self.user_data.get('fullname', self.username) if self.user_data else self.username
        
        if not self.user_data:
            print("No user data available to display profile")
            return
        
        # Update header info
        self.name_label.setText(self.fullname)
        self.username_label.setText(f"@{self.username}")
        
        # Update profile image
        self._refresh_profile_image()
        
        # Clear and rebuild form layouts
        self._clear_form_layouts()
        self._populate_personal_info()
        self._populate_employment_info()
    
    def _clear_form_layouts(self):
        """Clear all form layouts to rebuild them with fresh data"""
        # Keep track of which sections have data
        self.has_personal_data = False
        self.has_employment_data = False
        
        # Clear all rows from personal layout
        while self.personal_layout.rowCount() > 0:
            # Take the item at position (0,0) and (0,1)
            label_item = self.personal_layout.itemAt(0, QFormLayout.ItemRole.LabelRole)
            field_item = self.personal_layout.itemAt(0, QFormLayout.ItemRole.FieldRole)
            
            # Remove widgets if they exist
            if label_item and label_item.widget():
                label_widget = label_item.widget()
                self.personal_layout.removeWidget(label_widget)
                label_widget.deleteLater()
                
            if field_item and field_item.widget():
                field_widget = field_item.widget()
                self.personal_layout.removeWidget(field_widget)
                field_widget.deleteLater()
            
            # Remove the row
            self.personal_layout.removeRow(0)
            
        # Clear employment layout the same way
        while self.employment_layout.rowCount() > 0:
            # Take the item at position (0,0) and (0,1)
            label_item = self.employment_layout.itemAt(0, QFormLayout.ItemRole.LabelRole)
            field_item = self.employment_layout.itemAt(0, QFormLayout.ItemRole.FieldRole)
            
            # Remove widgets if they exist
            if label_item and label_item.widget():
                label_widget = label_item.widget()
                self.employment_layout.removeWidget(label_widget)
                label_widget.deleteLater()
                
            if field_item and field_item.widget():
                field_widget = field_item.widget()
                self.employment_layout.removeWidget(field_widget)
                field_widget.deleteLater()
            
            # Remove the row
            self.employment_layout.removeRow(0)
    
    def _populate_personal_info(self):
        """Populate personal information section with data"""
        # Style for value labels - using system palette colors
        value_style = "padding: 2px 4px; background-color: palette(alternateBase); border-radius: 3px; color: palette(text);"
        
        # Email
        email = self.user_data.get('email', '')
        if email:
            email_label = QLabel(email)
            email_label.setStyleSheet(value_style)
            self.personal_layout.addRow("Email:", email_label)
            self.has_personal_data = True
            
        # Phone number (WhatsApp)
        phone = self.user_data.get('phone_number', '')
        if phone:
            phone_label = QLabel(phone)
            phone_label.setStyleSheet(value_style)
            self.personal_layout.addRow("WhatsApp:", phone_label)
            self.has_personal_data = True
            
        # Gender
        gender = self.user_data.get('gender', '')
        if gender:
            gender_label = QLabel(gender)
            gender_label.setStyleSheet(value_style)
            self.personal_layout.addRow("Gender:", gender_label)
            self.has_personal_data = True
            
        # Birth date
        birth_date = self.user_data.get('birth_date', '')
        if birth_date:
            # Format the date nicely
            try:
                date_obj = QDate.fromString(birth_date, "yyyy-MM-dd")
                formatted_date = date_obj.toString("dd MMMM yyyy")
                birth_date_label = QLabel(formatted_date)
            except:
                birth_date_label = QLabel(birth_date)
                
            birth_date_label.setStyleSheet(value_style)
            self.personal_layout.addRow("Birth Date:", birth_date_label)
            self.has_personal_data = True
            
        # Address
        address = self.user_data.get('address', '')
        if address:
            address_label = QLabel(address)
            address_label.setStyleSheet(value_style)
            address_label.setWordWrap(True)
            self.personal_layout.addRow("Address:", address_label)
            self.has_personal_data = True
            
        # Show/hide personal section based on data availability
        self.personal_section.setVisible(self.has_personal_data)
    
    def _populate_employment_info(self):
        """Populate employment information section with data"""
        # Style for value labels - using system palette colors
        value_style = "padding: 2px 4px; background-color: palette(alternateBase); border-radius: 3px; color: palette(text);"
        
        # Department
        department = self.user_data.get('department', '')
        if department:
            department_label = QLabel(department)
            department_label.setStyleSheet(value_style)
            self.employment_layout.addRow("Department:", department_label)
            self.has_employment_data = True
            
        # Start date
        start_date = self.user_data.get('start_date', '')
        if start_date:
            # Format the date nicely
            try:
                date_obj = QDate.fromString(start_date, "yyyy-MM-dd")
                formatted_date = date_obj.toString("dd MMMM yyyy")
                start_date_label = QLabel(formatted_date)
            except:
                start_date_label = QLabel(start_date)
                
            start_date_label.setStyleSheet(value_style)
            self.employment_layout.addRow("Start Date:", start_date_label)
            self.has_employment_data = True
            
        # Bank name
        bank_name = self.user_data.get('bank_name', '')
        if bank_name:
            bank_name_label = QLabel(bank_name)
            bank_name_label.setStyleSheet(value_style)
            self.employment_layout.addRow("Bank Name:", bank_name_label)
            self.has_employment_data = True
            
        # Bank account number
        bank_account_number = self.user_data.get('bank_account_number', '')
        if bank_account_number:
            bank_account_number_label = QLabel(bank_account_number)
            bank_account_number_label.setStyleSheet(value_style)
            self.employment_layout.addRow("Account No:", bank_account_number_label)
            self.has_employment_data = True
            
        # Bank account holder
        bank_account_holder = self.user_data.get('bank_account_holder', '')
        if bank_account_holder:
            bank_account_holder_label = QLabel(bank_account_holder)
            bank_account_holder_label.setStyleSheet(value_style)
            self.employment_layout.addRow("Account Holder:", bank_account_holder_label)
            self.has_employment_data = True
            
        # Show/hide employment section based on data availability
        self.employment_section.setVisible(self.has_employment_data)
    
    def _refresh_profile_image(self):
        """Load and display the user's profile image"""
        from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QBrush, QColor
        import os
        
        # Check if user has a profile image
        profile_image_path = None
        if self.user_data and self.user_data.get('profile_image'):
            # Convert from relative to absolute path
            relative_path = self.user_data.get('profile_image')
            profile_image_path = self.db_handler.get_profile_image_path(relative_path)
        
        if profile_image_path and os.path.exists(profile_image_path):
            # User has a profile image, load it and make circular
            pixmap = QPixmap(profile_image_path)
            pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                Qt.TransformationMode.SmoothTransformation)
            
            # Create circular image
            rounded_pixmap = QPixmap(100, 100)
            rounded_pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Create circular path
            path = QPainterPath()
            path.addEllipse(0, 0, 100, 100)
            painter.setClipPath(path)
            
            # Draw the image
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            self.profile_image_label.setPixmap(rounded_pixmap)
        else:
            # No profile image, display colored circle with initials
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
            font.setPointSize(32)
            font.setBold(True)
            painter.setFont(font)
            
            rect = pixmap.rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)
            painter.end()
            
            self.profile_image_label.setPixmap(pixmap)
    
    def update_username(self, username):
        """Update the displayed username"""
        if self.username == username:
            return
            
        self.username = username
        self.refresh_data()