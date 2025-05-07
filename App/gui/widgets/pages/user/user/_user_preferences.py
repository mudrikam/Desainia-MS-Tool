from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, 
    QFileDialog, QGroupBox, QLineEdit, QFormLayout, QMessageBox,
    QCheckBox, QSizePolicy, QDateEdit, QComboBox, QTextEdit,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QPixmap, QColor, QPainter, QBrush
import qtawesome as qta
import os
import datetime

# Import the database module for user data
from App.core.database import UserDashboardDB


class UserPreferencesWidget(QWidget):
    """User preferences widget for the dashboard."""
    
    # Signal when image changes
    image_changed = pyqtSignal()
    
    def __init__(self, parent=None, username="User", app_instance=None):
        super().__init__(parent)
        self.username = username
        self.app = app_instance
        
        # Initialize database handler
        self.db_handler = UserDashboardDB(self.app)
        
        # Get user data from database
        self.user_data = self.db_handler.get_user_data(username, no_cache=True, include_profile=True)
        self.fullname = self.user_data.get('fullname', username) if self.user_data else username
        
        # Set up the UI
        self._setup_ui()
        
        # Refresh the UI with the latest data
        self.refresh_data()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget to hold all the form elements
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        
        # Profile image section
        profile_section = QGroupBox("Profile Image")
        profile_layout = QVBoxLayout(profile_section)
        profile_layout.setSpacing(10)
        
        # Current profile image display
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # Current profile image display
        current_image_label = QLabel("Current:")
        
        # Use a small circular label for preview
        self.current_image = QLabel()
        self.current_image.setFixedSize(50, 50)
        
        image_layout.addWidget(current_image_label)
        image_layout.addWidget(self.current_image)
        image_layout.addStretch()
        
        # Upload button
        image_buttons_container = QWidget()
        image_buttons_layout = QHBoxLayout(image_buttons_container)
        image_buttons_layout.setContentsMargins(0, 0, 0, 0)
        image_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align buttons to the left
        
        upload_btn = QPushButton("Upload New Image")
        upload_btn.setIcon(qta.icon("fa6s.upload"))
        upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        upload_btn.clicked.connect(self._upload_profile_image)
        upload_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)  # Prevent horizontal stretching
        
        remove_btn = QPushButton("Remove Image")
        remove_btn.setIcon(qta.icon("fa6s.trash"))
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(self._remove_profile_image)
        remove_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)  # Prevent horizontal stretching
        
        image_buttons_layout.addWidget(upload_btn)
        image_buttons_layout.addWidget(remove_btn)
        image_buttons_layout.addStretch()  # Add stretch after buttons to prevent them from expanding
        
        # Image requirements note
        image_note = QLabel("Note: Images will be resized to 200x200 pixels. Supported formats: JPG, PNG, BMP.")
        image_note.setStyleSheet("font-size: 11px; color: palette(mid); font-style: italic;")
        image_note.setWordWrap(True)
        
        # Add all elements to profile image section
        profile_layout.addWidget(image_container)
        profile_layout.addWidget(image_buttons_container)
        profile_layout.addWidget(image_note)
        
        # Add profile image section to content layout
        content_layout.addWidget(profile_section)
        
        # ============ PERSONAL INFORMATION ============
        personal_section = QGroupBox("Personal Information")
        personal_layout = QVBoxLayout(personal_section)
        personal_layout.setSpacing(15)
        
        # Fullname and Gender fields - side by side
        name_gender_container = QHBoxLayout()
        name_gender_container.setSpacing(15)
        
        # Full Name field
        fullname_form = QFormLayout()
        fullname_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.fullname_edit = QLineEdit()
        fullname_form.addRow("Full Name:", self.fullname_edit)
        name_gender_container.addLayout(fullname_form)
        
        # Gender field
        gender_form = QFormLayout()
        gender_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "Male", "Female", "Other", "Prefer not to say"])
        gender_form.addRow("Gender:", self.gender_combo)
        name_gender_container.addLayout(gender_form)
        
        personal_layout.addLayout(name_gender_container)
        
        # Username and Email fields - side by side
        username_email_container = QHBoxLayout()
        username_email_container.setSpacing(15)
        
        # Username field
        username_form = QFormLayout()
        username_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.username_edit = QLineEdit()
        username_form.addRow("Username:", self.username_edit)
        username_email_container.addLayout(username_form)
        
        # Email field
        email_form = QFormLayout()
        email_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.email_edit = QLineEdit()
        email_form.addRow("Email:", self.email_edit)
        username_email_container.addLayout(email_form)
        
        personal_layout.addLayout(username_email_container)
        
        # WhatsApp and Birth date - side by side
        whatsapp_birth_container = QHBoxLayout()
        whatsapp_birth_container.setSpacing(15)
        
        # WhatsApp number field
        whatsapp_form = QFormLayout()
        whatsapp_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+62")
        whatsapp_form.addRow("WhatsApp:", self.phone_edit)
        whatsapp_birth_container.addLayout(whatsapp_form)
        
        # Birth date field
        birth_date_form = QFormLayout()
        birth_date_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
        # We'll set a proper date in refresh_data() or clear it if no data exists
        self.birth_date_edit.setSpecialValueText(" ")  # Empty text for null date
        birth_date_form.addRow("Birth Date:", self.birth_date_edit)
        whatsapp_birth_container.addLayout(birth_date_form)
        
        personal_layout.addLayout(whatsapp_birth_container)
        
        # Address field
        address_form = QFormLayout()
        address_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        self.address_edit.setPlaceholderText("Enter your address here")
        address_form.addRow("Address:", self.address_edit)
        personal_layout.addLayout(address_form)
        
        content_layout.addWidget(personal_section)
        
        # ============ EMPLOYMENT INFORMATION ============
        employment_section = QGroupBox("Employment Information")
        employment_layout = QVBoxLayout(employment_section)
        employment_layout.setSpacing(15)
        
        # Department and Start date fields - side by side
        department_date_container = QHBoxLayout()
        department_date_container.setSpacing(15)
        
        # Department field
        department_form = QFormLayout()
        department_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.department_combo = QComboBox()
        self.department_combo.addItem("")  # Empty option
        # Load departments from database
        departments = self._get_departments()
        if departments:
            self.department_combo.addItems(departments)
        department_form.addRow("Department:", self.department_combo)
        department_date_container.addLayout(department_form)
        
        # Start date field
        start_date_form = QFormLayout()
        start_date_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd") 
        self.start_date_edit.setSpecialValueText(" ")  # Empty text for null date
        start_date_form.addRow("Start Date:", self.start_date_edit)
        department_date_container.addLayout(start_date_form)
        
        employment_layout.addLayout(department_date_container)
        
        # Add bank account information - bank name and account number
        bank_info_container = QHBoxLayout()
        bank_info_container.setSpacing(15)
        
        # Bank name field
        bank_name_form = QFormLayout()
        bank_name_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.bank_name_edit = QLineEdit()
        self.bank_name_edit.setPlaceholderText("e.g., BCA, BNI, BRI")
        bank_name_form.addRow("Bank Name:", self.bank_name_edit)
        bank_info_container.addLayout(bank_name_form)
        
        # Account number field
        account_number_form = QFormLayout()
        account_number_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.bank_account_number_edit = QLineEdit()
        self.bank_account_number_edit.setPlaceholderText("Enter account number")
        account_number_form.addRow("Account No:", self.bank_account_number_edit)
        bank_info_container.addLayout(account_number_form)
        
        employment_layout.addLayout(bank_info_container)
        
        # Account holder name
        account_holder_form = QFormLayout()
        account_holder_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.bank_account_holder_edit = QLineEdit()
        self.bank_account_holder_edit.setPlaceholderText("Enter account holder name")
        account_holder_form.addRow("Account Holder:", self.bank_account_holder_edit)
        
        employment_layout.addLayout(account_holder_form)
        
        content_layout.addWidget(employment_section)
        
        # ============ SECURITY SECTION ============
        security_section = QGroupBox("Security")
        security_layout = QVBoxLayout(security_section)
        security_layout.setSpacing(10)
        
        # Password fields - side by side
        password_container = QHBoxLayout()
        password_container.setSpacing(15)
        
        # New Password field
        password_form = QFormLayout()
        password_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_form.addRow("New Password:", self.password_edit)
        password_container.addLayout(password_form)
        
        # Confirm Password field
        confirm_password_form = QFormLayout()
        confirm_password_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_password_form.addRow("Confirm:", self.confirm_password_edit)
        password_container.addLayout(confirm_password_form)
        
        security_layout.addLayout(password_container)
        
        # Checkbox to show/hide password
        show_password_container = QHBoxLayout()
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.toggled.connect(self._toggle_password_visibility)
        show_password_container.addWidget(self.show_password_cb)
        show_password_container.addStretch()
        security_layout.addLayout(show_password_container)
        
        # Note about password
        password_note = QLabel("Leave password fields empty if you don't want to change it")
        password_note.setStyleSheet("font-size: 11px; color: palette(mid); font-style: italic;")
        security_layout.addWidget(password_note)
        
        content_layout.addWidget(security_section)
        
        # Save button
        save_button = QPushButton("Save Changes")
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.clicked.connect(self._save_user_info)
        
        # Center the save button
        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()
        save_button_layout.addWidget(save_button)
        save_button_layout.addStretch()
        
        content_layout.addLayout(save_button_layout)
        
        # Add spacer at the bottom
        content_layout.addStretch()
    
    def _get_departments(self):
        """Get list of departments from database"""
        if not self.db_handler:
            return []
            
        # Get departments list from database
        return self.db_handler.get_departments()
        
    def _toggle_password_visibility(self, show):
        """Toggle password visibility based on checkbox state"""
        mode = QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
        self.password_edit.setEchoMode(mode)
        self.confirm_password_edit.setEchoMode(mode)
        
    def _save_user_info(self):
        """Save user information to the database"""
        # Get values from form fields
        new_fullname = self.fullname_edit.text().strip()
        new_username = self.username_edit.text().strip()
        new_email = self.email_edit.text().strip()
        new_password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Get values from other fields
        new_phone = self.phone_edit.text().strip()
        new_address = self.address_edit.toPlainText().strip()
        new_gender = self.gender_combo.currentText()
        new_department = self.department_combo.currentText()
        
        # Get bank account information
        new_bank_name = self.bank_name_edit.text().strip()
        new_bank_account_number = self.bank_account_number_edit.text().strip()
        new_bank_account_holder = self.bank_account_holder_edit.text().strip()
        
        # Get date values - only if they're not empty
        birth_date = None
        if not self.birth_date_edit.specialValueText() or self.birth_date_edit.date() != self.birth_date_edit.minimumDate():
            birth_date = self.birth_date_edit.date().toString("yyyy-MM-dd")
            
        start_date = None
        if not self.start_date_edit.specialValueText() or self.start_date_edit.date() != self.start_date_edit.minimumDate():
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        
        # Validate input
        if not new_fullname:
            QMessageBox.warning(self, "Validation Error", "Full name cannot be empty.")
            return
            
        if not new_username:
            QMessageBox.warning(self, "Validation Error", "Username cannot be empty.")
            return
            
        if not new_email:
            QMessageBox.warning(self, "Validation Error", "Email cannot be empty.")
            return
        
        # Check if password fields match if either is filled
        if new_password or confirm_password:
            if new_password != confirm_password:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                return
        else:
            # If both password fields are empty, set to None to skip password update
            new_password = None
            
        # Get current user ID
        user_id = self.user_data.get('id')
        if not user_id:
            QMessageBox.critical(self, "Error", "Could not retrieve user ID.")
            return
            
        # Check if anything changed
        # For dates, we need to compare against the value in user_data or an empty string
        current_birth_date = self.user_data.get('birth_date', '') or ''
        current_start_date = self.user_data.get('start_date', '') or ''
        
        if (new_fullname == self.user_data.get('fullname', '') and
            new_username == self.user_data.get('username', '') and
            new_email == self.user_data.get('email', '') and
            new_phone == self.user_data.get('phone_number', '') and
            new_address == self.user_data.get('address', '') and
            new_gender == self.user_data.get('gender', '') and
            new_department == self.user_data.get('department', '') and
            new_bank_name == self.user_data.get('bank_name', '') and
            new_bank_account_number == self.user_data.get('bank_account_number', '') and
            new_bank_account_holder == self.user_data.get('bank_account_holder', '') and
            birth_date == current_birth_date and
            start_date == current_start_date and
            new_password is None):
            QMessageBox.information(self, "No Changes", "No changes were made.")
            return
            
        # Update user information in database
        success, message = self.db_handler.update_user_info(
            user_id, 
            fullname=new_fullname,
            username=new_username,
            email=new_email,
            password=new_password,
            phone_number=new_phone, 
            address=new_address,
            birth_date=birth_date,
            gender=new_gender,
            start_date=start_date,
            department=new_department,
            bank_name=new_bank_name,
            bank_account_number=new_bank_account_number,
            bank_account_holder=new_bank_account_holder
        )
        
        if success:
            QMessageBox.information(self, "Success", "User information updated successfully.")
            
            # Update local vars with the new username if it changed
            old_username = self.username
            if new_username != old_username:
                self.username = new_username
            
            # Explicitly fetch all data from database again to ensure we have the latest
            self.user_data = self.db_handler.get_user_data(self.username, no_cache=True, include_profile=True)
            
            # Refresh UI with new data
            self.refresh_data()
            
            # Emit signal to notify parent about user data change
            self.image_changed.emit()  # We can reuse this signal for all profile changes
        else:
            QMessageBox.critical(self, "Error", f"Failed to update user information: {message}")
            
    def refresh_data(self):
        """Refresh user data from database and update UI"""
        # Get fresh user data from database - include_profile=True to get all profile fields
        self.user_data = self.db_handler.get_user_data(self.username, no_cache=True, include_profile=True)
        self.fullname = self.user_data.get('fullname', self.username) if self.user_data else self.username
        
        # Update UI with fresh data
        self._refresh_profile_image()
        self._refresh_form_fields()
        
    def _refresh_profile_image(self):
        """Refresh the profile image shown in the preferences tab using fresh DB data"""
        if not hasattr(self, 'current_image'):
            return
        
        # Check if user has a profile image (using fresh data from DB)
        profile_image_path = None
        if self.user_data and self.user_data.get('profile_image'):
            # Convert from relative to absolute path
            relative_path = self.user_data.get('profile_image')
            profile_image_path = self.db_handler.get_profile_image_path(relative_path)
        
        if profile_image_path and os.path.exists(profile_image_path):
            # User has a profile image, load it and make circular
            pixmap = QPixmap(profile_image_path)
            pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                Qt.TransformationMode.SmoothTransformation)
            
            # Create circular mask
            mask = QPixmap(50, 50)
            mask.fill(Qt.GlobalColor.transparent)
            painter = QPainter(mask)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, 50, 50)
            painter.end()
            
            # Apply mask
            result = QPixmap(pixmap.size())
            result.fill(Qt.GlobalColor.transparent)
            painter = QPainter(result)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.drawPixmap(0, 0, mask)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            self.current_image.setPixmap(result)
            self.current_image.setStyleSheet("border: none;")
        else:
            # No profile image, display colored circle with initials
            pixmap = QPixmap(50, 50)
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
            painter.drawEllipse(0, 0, 50, 50)
            
            # Draw text
            painter.setPen(Qt.GlobalColor.white)
            font = painter.font()
            font.setPointSize(16)
            font.setBold(True)
            painter.setFont(font)
            
            rect = pixmap.rect()
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)
            painter.end()
            
            self.current_image.setPixmap(pixmap)
            self.current_image.setStyleSheet("border: none;")
    
    def _refresh_form_fields(self):
        """Refresh form fields with current user data"""
        if not self.user_data:
            return
            
        # Update form fields with current values
        self.fullname_edit.setText(self.user_data.get('fullname', ''))
        self.username_edit.setText(self.user_data.get('username', ''))
        self.email_edit.setText(self.user_data.get('email', ''))
        
        # Update WhatsApp field
        phone = self.user_data.get('phone_number', '')
        self.phone_edit.setText(phone)
        
        # Set address
        address = self.user_data.get('address', '')
        if address:
            self.address_edit.setText(address)
        else:
            self.address_edit.clear()
            
        # Set gender selection
        gender = self.user_data.get('gender', '')
        index = self.gender_combo.findText(gender)
        if index >= 0:
            self.gender_combo.setCurrentIndex(index)
        else:
            self.gender_combo.setCurrentIndex(0)  # Empty selection
            
        # Set department selection
        department = self.user_data.get('department', '')
        index = self.department_combo.findText(department)
        if index >= 0:
            self.department_combo.setCurrentIndex(index)
        else:
            self.department_combo.setCurrentIndex(0)  # Empty selection
            
        # Set bank account fields
        bank_name = self.user_data.get('bank_name', '')
        bank_account_number = self.user_data.get('bank_account_number', '')
        bank_account_holder = self.user_data.get('bank_account_holder', '')
        
        self.bank_name_edit.setText(bank_name)
        self.bank_account_number_edit.setText(bank_account_number)
        self.bank_account_holder_edit.setText(bank_account_holder)
            
        # Handle birth date specially - don't set a default if no data
        birth_date_str = self.user_data.get('birth_date', '')
        if birth_date_str:
            try:
                birth_date = QDate.fromString(birth_date_str, "yyyy-MM-dd")
                if birth_date.isValid():
                    self.birth_date_edit.setDate(birth_date)
                else:
                    self.birth_date_edit.setDate(self.birth_date_edit.minimumDate())
            except Exception as e:
                # Clear the date if parsing fails
                self.birth_date_edit.setDate(self.birth_date_edit.minimumDate())
        else:
            # Clear the date if no data
            self.birth_date_edit.setDate(self.birth_date_edit.minimumDate())
                
        # Handle start date specially - don't set a default if no data
        start_date_str = self.user_data.get('start_date', '')
        if start_date_str:
            try:
                start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")
                if start_date.isValid():
                    self.start_date_edit.setDate(start_date)
                else:
                    self.start_date_edit.setDate(self.start_date_edit.minimumDate())
            except Exception as e:
                # Clear the date if parsing fails
                self.start_date_edit.setDate(self.start_date_edit.minimumDate())
        else:
            # Clear the date if no data
            self.start_date_edit.setDate(self.start_date_edit.minimumDate())
                
        # Clear password fields
        self.password_edit.clear()
        self.confirm_password_edit.clear()
    
    def _upload_profile_image(self):
        """Handle profile image upload"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setWindowTitle("Select Profile Image")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                
                # Save image to UserData/profile_images directory
                success = self.db_handler.save_profile_image(self.username, image_path)
                
                if success:
                    # Refresh data directly from database after upload
                    self.refresh_data()
                    
                    # Emit signal to notify parent about image change
                    self.image_changed.emit()
    
    def _remove_profile_image(self):
        """Handle profile image removal"""
        success = self.db_handler.delete_profile_image(self.username)
        
        if success:
            # Refresh data directly from database after removal
            self.refresh_data()
            
            # Emit signal to notify parent about image change
            self.image_changed.emit()
    
    def update_username(self, username):
        """Update the displayed username"""
        if self.username == username:
            return
            
        self.username = username
        self.refresh_data()