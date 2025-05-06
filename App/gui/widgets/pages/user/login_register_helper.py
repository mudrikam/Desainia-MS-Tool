from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QHBoxLayout, QFrame, QCheckBox,
                            QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta
import os
import re

class LoginRegisterWidget(QWidget):
    """Login and registration widget that can be used as a helper component."""
    
    # Define signals
    login_successful = pyqtSignal(dict)  # Emits user data when login succeeds
    register_successful = pyqtSignal(dict)  # Emits user data when registration succeeds
    
    # Centralized styles
    STYLES = {
        # Common colors
        "colors": {
            "primary": "palette(highlight)",
            "primary_hover": "#0366d6",
            "primary_pressed": "#024ea2",
            "danger": "#e03131",
            "danger_bg": "rgba(224, 49, 49, 0.1)",
            "border": "rgba(0, 0, 0, 0.1)",
            "transparent": "rgba(0, 0, 0, 0.01)",
        },
        
        # Form elements
        "container": """
            QFrame#login_container {
                background-color: rgba(0, 0, 0, 0.01);
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """,
        
        "title": """
            font-size: 24px;
            font-weight: 500;
            color: palette(text);
            margin-top: 10px;
            margin-bottom: 20px;
        """,
        
        "input": """
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 5px;
                padding: 8px 15px;
                background-color: palette(base);
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid palette(highlight);
            }
        """,
        
        "button_primary": """
            QPushButton {
                background-color: palette(highlight);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0366d6;
            }
            QPushButton:pressed {
                background-color: #024ea2;
            }
        """,
        
        "button_link": """
            QPushButton {
                border: none;
                font-size: 13px;
                color: palette(link);
                padding: 0 3px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """,
        
        "checkbox": """
            QCheckBox {
                font-size: 13px;
                color: palette(text);
            }
        """,
        
        "error_message": """
            font-size: 13px;
            color: #e03131;
            background-color: rgba(224, 49, 49, 0.1);
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 5px;
            border-left: 3px solid #e03131;
        """,
        
        "text_label": """
            font-size: 13px; 
            color: palette(text);
        """
    }
    
    def __init__(self, parent=None, auth=None):
        super().__init__(parent)
        
        # Get app instance and translation helper
        from PyQt6.QtWidgets import QApplication
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation
        
        # Store auth helper
        self.auth = auth
        
        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a centered login container
        container = QFrame()
        container.setObjectName("login_container")
        container.setFixedWidth(400)
        container.setStyleSheet(self.STYLES["container"])
        
        # Container layout
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 40, 30, 40)
        container_layout.setSpacing(20)
        
        # Create a stacked widget to switch between login, register, and forgot password forms
        self.stacked_widget = QStackedWidget()
        
        # Create login form
        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(20)
        
        # Create register form
        register_widget = QWidget()
        register_layout = QVBoxLayout(register_widget)
        register_layout.setContentsMargins(0, 0, 0, 0)
        register_layout.setSpacing(20)
        
        # Create forgot password form
        forgot_widget = QWidget()
        forgot_layout = QVBoxLayout(forgot_widget)
        forgot_layout.setContentsMargins(0, 0, 0, 0)
        forgot_layout.setSpacing(20)
        
        # Add all forms to stacked widget
        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)
        self.stacked_widget.addWidget(forgot_widget)
        
        # ===== LOGIN FORM =====
        
        # Simplified title section for login - removed user icon
        login_title_layout = QVBoxLayout()
        login_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title label
        login_title = QLabel(self.tr('page', 'user', 'title'))
        login_title.setStyleSheet(self.STYLES["title"])
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_title_layout.addWidget(login_title)
        
        # Form section for login
        login_form_layout = QVBoxLayout()
        login_form_layout.setSpacing(15)
        
        # Error message label for login
        self.login_error_label = QLabel("")
        self.login_error_label.setStyleSheet(self.STYLES["error_message"])
        self.login_error_label.setWordWrap(True)
        self.login_error_label.setVisible(False)
        login_form_layout.addWidget(self.login_error_label)
        
        # Username field
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText(self.tr('page', 'user', 'username'))
        self.username_field.setProperty("class", "login-input")
        self.username_field.setMinimumHeight(40)
        self.username_field.setStyleSheet(self.STYLES["input"])
        # Connect Enter key press
        self.username_field.returnPressed.connect(self._on_login)
        
        # Password field
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText(self.tr('page', 'user', 'password'))
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setProperty("class", "login-input")
        self.password_field.setMinimumHeight(40)
        self.password_field.setStyleSheet(self.STYLES["input"])
        # Connect Enter key press
        self.password_field.returnPressed.connect(self._on_login)
        
        # Remember me and forgot password row
        options_layout = QHBoxLayout()
        
        self.remember_me = QCheckBox(self.tr('page', 'user', 'remember_me'))
        self.remember_me.setStyleSheet(self.STYLES["checkbox"])
        
        # Load remember_me setting
        try:
            settings = self.auth.settings
            self.remember_me.setChecked(settings.get("remember_login", False))
        except:
            self.remember_me.setChecked(False)
        
        forgot_password = QPushButton(self.tr('page', 'user', 'forgot_password'))
        forgot_password.setFlat(True)
        forgot_password.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_password.setStyleSheet(self.STYLES["button_link"])
        
        options_layout.addWidget(self.remember_me)
        options_layout.addStretch()
        options_layout.addWidget(forgot_password)
        
        # Login button
        login_btn = QPushButton(self.tr('page', 'user', 'signin_button'))
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet(self.STYLES["button_primary"])
        
        # Register link
        login_register_layout = QHBoxLayout()
        login_register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_register_text = QLabel(self.tr('page', 'user', 'no_account'))
        login_register_text.setStyleSheet(self.STYLES["text_label"])
        
        login_register_btn = QPushButton(self.tr('page', 'user', 'register'))
        login_register_btn.setFlat(True)
        login_register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_register_btn.setStyleSheet(self.STYLES["button_link"])
        
        login_register_layout.addWidget(login_register_text)
        login_register_layout.addWidget(login_register_btn)
        
        # Add form elements to login layout
        login_form_layout.addWidget(self.username_field)
        login_form_layout.addWidget(self.password_field)
        login_form_layout.addLayout(options_layout)
        login_form_layout.addWidget(login_btn)
        login_form_layout.addSpacing(5)
        login_form_layout.addLayout(login_register_layout)
        
        # Add title and form to login widget
        login_layout.addLayout(login_title_layout)
        login_layout.addLayout(login_form_layout)
        
        # === REGISTER FORM ===
        # Simplified title section for register - removed user icon
        register_title_layout = QVBoxLayout()
        register_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Register title
        register_title = QLabel(self.tr('page', 'user', 'register_title'))
        register_title.setStyleSheet(self.STYLES["title"])
        register_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        register_title_layout.addWidget(register_title)
        
        # Form section for register
        register_form_layout = QVBoxLayout()
        register_form_layout.setSpacing(15)
        
        # Error message label for registration
        self.register_error_label = QLabel("")
        self.register_error_label.setStyleSheet(self.STYLES["error_message"])
        self.register_error_label.setWordWrap(True)
        self.register_error_label.setVisible(False)
        register_form_layout.addWidget(self.register_error_label)

        # Name field
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText(self.tr('page', 'user', 'fullname'))
        self.name_field.setProperty("class", "register-input")
        self.name_field.setMinimumHeight(40)
        self.name_field.setStyleSheet(self.STYLES["input"])
        self.name_field.returnPressed.connect(self._on_register)
        
        # Email field
        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText(self.tr('page', 'user', 'email'))
        self.email_field.setProperty("class", "register-input")
        self.email_field.setMinimumHeight(40)
        self.email_field.setStyleSheet(self.STYLES["input"])
        self.email_field.returnPressed.connect(self._on_register)
        
        # Register username field
        self.reg_username_field = QLineEdit()
        self.reg_username_field.setPlaceholderText(self.tr('page', 'user', 'register_username'))
        self.reg_username_field.setProperty("class", "register-input")
        self.reg_username_field.setMinimumHeight(40)
        self.reg_username_field.setStyleSheet(self.STYLES["input"])
        self.reg_username_field.returnPressed.connect(self._on_register)
        
        # Register password field
        self.reg_password_field = QLineEdit()
        self.reg_password_field.setPlaceholderText(self.tr('page', 'user', 'register_password'))
        self.reg_password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_field.setProperty("class", "register-input")
        self.reg_password_field.setMinimumHeight(40)
        self.reg_password_field.setStyleSheet(self.STYLES["input"])
        self.reg_password_field.returnPressed.connect(self._on_register)
        
        # Register button
        register_btn = QPushButton(self.tr('page', 'user', 'create_account_button'))
        register_btn.setMinimumHeight(45)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setStyleSheet(self.STYLES["button_primary"])
        
        # Back to login link
        back_login_layout = QHBoxLayout()
        back_login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        back_login_text = QLabel(self.tr('page', 'user', 'have_account'))
        back_login_text.setStyleSheet(self.STYLES["text_label"])
        
        register_back_login_btn = QPushButton(self.tr('page', 'user', 'login'))
        register_back_login_btn.setFlat(True)
        register_back_login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_back_login_btn.setStyleSheet(self.STYLES["button_link"])
        
        back_login_layout.addWidget(back_login_text)
        back_login_layout.addWidget(register_back_login_btn)
        
        # Add form elements to register layout
        register_form_layout.addWidget(self.name_field)
        register_form_layout.addWidget(self.email_field)
        register_form_layout.addWidget(self.reg_username_field)
        register_form_layout.addWidget(self.reg_password_field)
        register_form_layout.addWidget(register_btn)
        register_form_layout.addSpacing(5)
        register_form_layout.addLayout(back_login_layout)
        
        # Add title and form to register widget
        register_layout.addLayout(register_title_layout)
        register_layout.addLayout(register_form_layout)
        
        # === FORGOT PASSWORD FORM ===
        # Title section for forgot password
        forgot_title_layout = QVBoxLayout()
        forgot_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Forgot password title
        forgot_title = QLabel("Reset Password")
        forgot_title.setStyleSheet(self.STYLES["title"])
        forgot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        forgot_title_layout.addWidget(forgot_title)
        
        # Form section for forgot password
        forgot_form_layout = QVBoxLayout()
        forgot_form_layout.setSpacing(15)
        
        # Status message for forgot password
        self.reset_status = QLabel("")
        self.reset_status.setStyleSheet(self.STYLES["error_message"])
        self.reset_status.setWordWrap(True)
        self.reset_status.setVisible(False)
        forgot_form_layout.addWidget(self.reset_status)
        
        # Email field
        self.reset_email_field = QLineEdit()
        self.reset_email_field.setPlaceholderText("Email Address")
        self.reset_email_field.setMinimumHeight(40)
        self.reset_email_field.setStyleSheet(self.STYLES["input"])
        
        # New password field
        self.new_password_field = QLineEdit()
        self.new_password_field.setPlaceholderText("New Password")
        self.new_password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_field.setMinimumHeight(40)
        self.new_password_field.setStyleSheet(self.STYLES["input"])
        
        # Confirm password field
        self.confirm_password_field = QLineEdit()
        self.confirm_password_field.setPlaceholderText("Confirm Password")
        self.confirm_password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_field.setMinimumHeight(40)
        self.confirm_password_field.setStyleSheet(self.STYLES["input"])
        
        # Reset button
        reset_btn = QPushButton("Reset Password")
        reset_btn.setMinimumHeight(45)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(self.STYLES["button_primary"])
        
        # Back to login link
        back_login_layout = QHBoxLayout()
        back_login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        back_login_btn = QPushButton("Back to Login")
        back_login_btn.setFlat(True)
        back_login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_login_btn.setStyleSheet(self.STYLES["button_link"])
        
        back_login_layout.addWidget(back_login_btn)
        
        # Add form elements to forgot password layout
        forgot_form_layout.addWidget(self.reset_email_field)
        forgot_form_layout.addWidget(self.new_password_field)
        forgot_form_layout.addWidget(self.confirm_password_field)
        forgot_form_layout.addWidget(reset_btn)
        forgot_form_layout.addSpacing(5)
        forgot_form_layout.addLayout(back_login_layout)
        
        # Add title and form to forgot password widget
        forgot_layout.addLayout(forgot_title_layout)
        forgot_layout.addLayout(forgot_form_layout)
        
        # Add stacked widget to container
        container_layout.addWidget(self.stacked_widget)
        
        # Center the container in the main layout
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(container)
        center_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        
        # Connect signals for login form
        login_btn.clicked.connect(self._on_login)
        forgot_password.clicked.connect(self._switch_to_forgot_password)
        login_register_btn.clicked.connect(self._switch_to_register)
        
        # Connect signals for register form
        register_btn.clicked.connect(self._on_register)
        register_back_login_btn.clicked.connect(self._switch_to_login)
        
        # Connect signals for forgot password form
        reset_btn.clicked.connect(self._on_reset_password)
        back_login_btn.clicked.connect(self._switch_to_login)
        
        # Start with login form
        self.stacked_widget.setCurrentIndex(0)

    def reset_login_form(self):
        """Reset the login form fields and checkbox"""
        # Clear the username and password fields
        self.username_field.clear()
        self.password_field.clear()
        
        # Uncheck the remember me checkbox
        self.remember_me.setChecked(False)
        
        # Hide any error messages
        self.login_error_label.setVisible(False)
        self.login_error_label.setText("")
        
        # Switch to login form if we're on register form
        self.stacked_widget.setCurrentIndex(0)
        
        # Update the remember_login setting
        if self.auth:
            try:
                self.auth.update_settings(remember_login=False)
            except Exception as e:
                print(f"Error resetting login form: {e}")

    def _on_login(self):
        """Handle login button click"""
        if not self.auth:
            print("Error: Auth helper not provided")
            return
            
        username = self.username_field.text()
        password = self.password_field.text()
        
        # Save remember me preference
        try:
            remember_me_checked = self.remember_me.isChecked()
            self.auth.update_settings(remember_login=remember_me_checked)
        except Exception as e:
            print(f"Error saving remember me setting: {e}")
        
        # Authenticate user
        user = self.auth.authenticate(username, password)
        
        if user:
            print(f"Login successful for user: {username}")
            self.login_successful.emit(user)
        else:
            print("Login failed. Invalid username or password.")
            self.login_error_label.setText("Invalid username or password.")
            self.login_error_label.setVisible(True)
    
    def _on_forgot_password(self):
        """Handle forgot password link click"""
        self._switch_to_forgot_password()
    
    def _on_register(self):
        """Handle register button click"""
        if not self.auth:
            print("Error: Auth helper not provided")
            return
            
        name = self.name_field.text()
        email = self.email_field.text()
        username = self.reg_username_field.text()
        password = self.reg_password_field.text()
        
        # Validate inputs
        if not all([name.strip(), email.strip(), username.strip(), password.strip()]):
            self.register_error_label.setText("Please fill in all fields.")
            self.register_error_label.setVisible(True)
            return
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.register_error_label.setText("Invalid email address.")
            self.register_error_label.setVisible(True)
            return
        
        # Register user
        success, message = self.auth.register(username, password, name, email)
        
        if success:
            print(f"Registration successful for {name} ({email})")
            
            # Switch to login screen with success message
            self._switch_to_login()
            
            # Auto-fill the login form
            self.username_field.setText(username)
            self.password_field.setText(password)
            
            # Get the newly registered user
            user = self.auth.get_current_user()
            if user:
                self.register_successful.emit(user)
        else:
            print(f"Registration failed: {message}")
            self.register_error_label.setText(message)
            self.register_error_label.setVisible(True)
    
    def _switch_to_register(self):
        """Switch to register form"""
        self.stacked_widget.setCurrentIndex(1)
        self.register_error_label.setVisible(False)
        
    def _switch_to_login(self):
        """Switch to login form"""
        self.stacked_widget.setCurrentIndex(0)
        self.login_error_label.setVisible(False)
    
    def _switch_to_forgot_password(self):
        """Switch to forgot password form"""
        self.stacked_widget.setCurrentIndex(2)
        self.reset_status.setVisible(False)
        self.reset_email_field.clear()
        self.new_password_field.clear()
        self.confirm_password_field.clear()
    
    def _on_reset_password(self):
        """Handle reset password button click"""
        if not self.auth:
            print("Error: Auth helper not provided")
            return
            
        email = self.reset_email_field.text()
        new_password = self.new_password_field.text()
        confirm_password = self.confirm_password_field.text()
        
        # Validate inputs
        if not all([email.strip(), new_password.strip(), confirm_password.strip()]):
            self.reset_status.setText("Please fill in all fields")
            self.reset_status.setVisible(True)
            return
        
        # Reset password
        success, message = self.auth.reset_password(email, new_password, confirm_password)
        
        if success:
            print(f"Password reset successful for {email}")
            
            # Get the user by email
            user = self.auth.get_user_by_email(email)
            
            if user:
                # Try to login with new credentials
                username = user.get('username')
                logged_in_user = self.auth.authenticate(username, new_password)
                
                if logged_in_user:
                    # Switch to login screen with success message
                    self._switch_to_login()
                    
                    # Emit login successful signal
                    self.login_successful.emit(logged_in_user)
                else:
                    # Just switch to login screen
                    self._switch_to_login()
                    
                    # Auto-fill the login form with username
                    self.username_field.setText(username)
                    self.password_field.setText("")
            else:
                # Just switch to login screen
                self._switch_to_login()
        else:
            # Show error message
            self.reset_status.setText(message)
            self.reset_status.setVisible(True)
            print(f"Password reset failed: {message}")
