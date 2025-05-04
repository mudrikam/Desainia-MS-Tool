from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QHBoxLayout, QFrame, QCheckBox,
                            QSpacerItem, QSizePolicy, QApplication, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import qtawesome as qta

class UserPage(QWidget):
    """User account page for managing user preferences and settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get app instance and translation helper
        self.app = QApplication.instance()
        self.tr = self.app.BASE_DIR.get_translation
        
        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a centered login container
        container = QFrame()
        container.setObjectName("login_container")
        container.setFixedWidth(400)
        container.setStyleSheet("""
            QFrame#login_container {
                background-color: rgba(0, 0, 0, 0.01);
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Container layout
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 40, 30, 40)
        container_layout.setSpacing(20)
        
        # Create a stacked widget to switch between login and register forms
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
        
        # Add both forms to stacked widget
        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)
        
        # ===== LOGIN FORM =====
        
        # Logo and title section for login
        login_title_layout = QVBoxLayout()
        login_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # User icon
        login_user_icon = QLabel()
        login_user_icon.setPixmap(qta.icon("fa6s.user", color="#0366d6").pixmap(64, 64))
        login_user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title label
        login_title = QLabel(self.tr('page', 'user', 'title'))
        login_title.setStyleSheet("""
            font-size: 24px;
            font-weight: 500;
            color: palette(text);
            margin-top: 10px;
            margin-bottom: 20px;
        """)
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_title_layout.addWidget(login_user_icon)
        login_title_layout.addWidget(login_title)
        
        # Form section for login
        login_form_layout = QVBoxLayout()
        login_form_layout.setSpacing(15)
        
        # Username field
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText(self.tr('page', 'user', 'username'))
        self.username_field.setProperty("class", "login-input")
        self.username_field.setMinimumHeight(40)
        self.username_field.setStyleSheet("""
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
        """)
        
        # Password field
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText(self.tr('page', 'user', 'password'))
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setProperty("class", "login-input")
        self.password_field.setMinimumHeight(40)
        self.password_field.setStyleSheet("""
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
        """)
        
        # Remember me and forgot password row
        options_layout = QHBoxLayout()
        
        remember_me = QCheckBox(self.tr('page', 'user', 'remember_me'))
        remember_me.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: palette(text);
            }
        """)
        
        forgot_password = QPushButton(self.tr('page', 'user', 'forgot_password'))
        forgot_password.setFlat(True)
        forgot_password.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_password.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 13px;
                color: palette(link);
                text-align: right;
                padding: 0;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        options_layout.addWidget(remember_me)
        options_layout.addStretch()
        options_layout.addWidget(forgot_password)
        
        # Login button
        login_btn = QPushButton(self.tr('page', 'user', 'signin_button'))
        login_btn.setMinimumHeight(45)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
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
        """)
        
        # Register link
        login_register_layout = QHBoxLayout()
        login_register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_register_text = QLabel(self.tr('page', 'user', 'no_account'))
        login_register_text.setStyleSheet("font-size: 13px; color: palette(text);")
        
        login_register_btn = QPushButton(self.tr('page', 'user', 'register'))
        login_register_btn.setFlat(True)
        login_register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_register_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 13px;
                color: palette(link);
                padding: 0 3px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
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
        
        # ===== REGISTER FORM =====
        
        # Logo and title section for register
        register_title_layout = QVBoxLayout()
        register_title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # User icon for register
        register_user_icon = QLabel()
        register_user_icon.setPixmap(qta.icon("fa6s.user-plus", color="#0366d6").pixmap(64, 64))
        register_user_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Register title
        register_title = QLabel(self.tr('page', 'user', 'register_title'))
        register_title.setStyleSheet("""
            font-size: 24px;
            font-weight: 500;
            color: palette(text);
            margin-top: 10px;
            margin-bottom: 20px;
        """)
        register_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        register_title_layout.addWidget(register_user_icon)
        register_title_layout.addWidget(register_title)
        
        # Form section for register
        register_form_layout = QVBoxLayout()
        register_form_layout.setSpacing(15)
        
        # Name field
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText(self.tr('page', 'user', 'fullname'))
        self.name_field.setProperty("class", "register-input")
        self.name_field.setMinimumHeight(40)
        self.name_field.setStyleSheet("""
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
        """)
        
        # Email field
        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText(self.tr('page', 'user', 'email'))
        self.email_field.setProperty("class", "register-input")
        self.email_field.setMinimumHeight(40)
        self.email_field.setStyleSheet("""
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
        """)
        
        # Register username field
        self.reg_username_field = QLineEdit()
        self.reg_username_field.setPlaceholderText(self.tr('page', 'user', 'register_username'))
        self.reg_username_field.setProperty("class", "register-input")
        self.reg_username_field.setMinimumHeight(40)
        self.reg_username_field.setStyleSheet("""
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
        """)
        
        # Register password field
        self.reg_password_field = QLineEdit()
        self.reg_password_field.setPlaceholderText(self.tr('page', 'user', 'register_password'))
        self.reg_password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password_field.setProperty("class", "register-input")
        self.reg_password_field.setMinimumHeight(40)
        self.reg_password_field.setStyleSheet("""
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
        """)
        
        # Register button
        register_btn = QPushButton(self.tr('page', 'user', 'create_account_button'))
        register_btn.setMinimumHeight(45)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setStyleSheet("""
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
        """)
        
        # Back to login link
        back_login_layout = QHBoxLayout()
        back_login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        back_login_text = QLabel(self.tr('page', 'user', 'have_account'))
        back_login_text.setStyleSheet("font-size: 13px; color: palette(text);")
        
        back_login_btn = QPushButton(self.tr('page', 'user', 'login'))
        back_login_btn.setFlat(True)
        back_login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_login_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 13px;
                color: palette(link);
                padding: 0 3px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        back_login_layout.addWidget(back_login_text)
        back_login_layout.addWidget(back_login_btn)
        
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
        forgot_password.clicked.connect(self._on_forgot_password)
        login_register_btn.clicked.connect(self._switch_to_register)
        
        # Connect signals for register form
        register_btn.clicked.connect(self._on_register)
        back_login_btn.clicked.connect(self._switch_to_login)
        
        # Start with login form
        self.stacked_widget.setCurrentIndex(0)
    
    def _on_login(self):
        """Handle login button click"""
        username = self.username_field.text()
        password = self.password_field.text()
        print(f"Login attempted with username: {username}")
        
        # Very simple validation - just check if fields are not empty
        if username.strip() and password.strip():
            # Get the main window
            main_window = self.window()
            if hasattr(main_window, 'content'):
                # Import the user profile page
                from .user_page import UserProfilePage
                
                # Get the content widget
                content_widget = main_window.content
                
                # Create the user profile page if it doesn't exist
                if 'user_profile' not in content_widget.pages:
                    profile_page = UserProfilePage(content_widget, username=username)
                    content_widget.add_page('user_profile', profile_page)
                else:
                    # Update the username if the page already exists
                    profile_page = content_widget.pages['user_profile']
                    # You'd need to add a method to update the username
                
                # Show the user profile page
                content_widget.show_page('user_profile')
        else:
            # In a real app, you'd show an error message to the user
            print("Please enter username and password")
    
    def _on_forgot_password(self):
        """Handle forgot password link click"""
        print("Forgot password clicked")
        # Add forgot password logic here
        
    def _on_register(self):
        """Handle register button click"""
        name = self.name_field.text()
        email = self.email_field.text()
        username = self.reg_username_field.text()
        password = self.reg_password_field.text()
        print(f"Registration attempted for {name} ({email})")
        # Add actual registration logic here
        
    def _switch_to_register(self):
        """Switch to register form"""
        self.stacked_widget.setCurrentIndex(1)
        
    def _switch_to_login(self):
        """Switch to login form"""
        self.stacked_widget.setCurrentIndex(0)
