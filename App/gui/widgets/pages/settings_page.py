from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QComboBox, QPushButton,
                           QTabWidget, QFrame, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt
import qtawesome as qta

class SettingsSection(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)
        self.layout.setSpacing(15)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(title_label)
        
        # Form layout for settings
        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.layout.addLayout(self.form)

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Add settings tabs
        self.tabs.addTab(self._create_general_tab(), "General")
        self.tabs.addTab(self._create_appearance_tab(), "Appearance")
        self.tabs.addTab(self._create_account_tab(), "Account")
        
        # Add save button at bottom
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 10, 20, 10)
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        self.layout.addWidget(button_container)
    
    def _create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Application section
        app_section = SettingsSection("Application Settings")
        app_section.form.addRow("Default Directory:", QLineEdit())
        app_section.form.addRow("Auto Save:", QCheckBox("Enable auto save"))
        app_section.form.addRow("Auto Save Interval:", QSpinBox())
        layout.addWidget(app_section)
        
        # Updates section
        update_section = SettingsSection("Updates")
        update_section.form.addRow("Check for Updates:", QComboBox())
        update_section.form.addRow("Auto Install Updates:", QCheckBox("Install updates automatically"))
        layout.addWidget(update_section)
        
        layout.addStretch()
        return tab
    
    def _create_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme section
        theme_section = SettingsSection("Theme Settings")
        theme_section.form.addRow("Theme:", QComboBox())
        theme_section.form.addRow("Custom Colors:", QPushButton("Customize..."))
        layout.addWidget(theme_section)
        
        # Interface section
        ui_section = SettingsSection("Interface")
        ui_section.form.addRow("Font Size:", QComboBox())
        ui_section.form.addRow("Show Toolbar:", QCheckBox("Display toolbar"))
        ui_section.form.addRow("Show Status Bar:", QCheckBox("Display status bar"))
        layout.addWidget(ui_section)
        
        layout.addStretch()
        return tab
    
    def _create_account_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Profile section
        profile_section = SettingsSection("Profile Settings")
        profile_section.form.addRow("Username:", QLineEdit())
        profile_section.form.addRow("Email:", QLineEdit())
        layout.addWidget(profile_section)
        
        # API section
        api_section = SettingsSection("API Settings")
        api_section.form.addRow("API Key:", QLineEdit())
        api_section.form.addRow("API URL:", QLineEdit())
        layout.addWidget(api_section)
        
        layout.addStretch()
        return tab
    
    def save_settings(self):
        # TODO: Implement settings saving
        pass
