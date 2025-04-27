# ---------------------------------------------------------------
# Copyright (C) 2025 M. Mudrikul Hikam
# ---------------------------------------------------------------
# This program is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License v3
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------
# Please do not remove this header.
# If you want to contribute, add your name here.
# ---------------------------------------------------------------
# | Contributor Name       | Contribution                       |
# |------------------------|------------------------------------|
# |                        |                                    |
# |                        |                                    |
# |                        |                                    |
# ---------------------------------------------------------------
#
# ---------------------------------------------------------------
# Trademark Notice
# ---------------------------------------------------------------
# "Desainia" is a trademark of M. Mudrikul Hikam.
# The use of the name "Desainia", the Desainia logo, and the 
# mascot character "Krea" is not permitted in redistributed or 
# modified versions of this software without explicit written 
# permission from the trademark holder.
#
# While this software is licensed under GPL v3, this does not 
# grant rights to use the "Desainia" brand identity in any form.
#
# Unauthorized use of these trademarks may constitute trademark 
# infringement under applicable law.
# ---------------------------------------------------------------

# This main initializes and runs the Desainia-MS-Tool application
# by creating an instance of MainWindow class from App.window module

import sys
import os

# Use os.path.join for cross-platform path handling
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from App.gui.window import MainWindow

# Base directory helper
class PathHelper:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._load_config()
        self._load_translations()
    
    def get_path(self, *paths):
        """Get absolute path relative to project root"""
        return os.path.join(self.base_dir, *paths)
    
    def _load_config(self):
        """Load main configuration"""
        import json
        config_path = self.get_path('App', 'config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
    def _load_translations(self):
        """Load language translations"""
        import json
        translation_path = self.get_path('App', 'config', 'translation.json')
        with open(translation_path, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)
            
    def get_translation(self, *keys):
        """Get translated text for current language"""
        current = self.translations.get(self.config['application']['language'], {})
        for key in keys:
            current = current.get(key, key)
        return current

# Initialize path helper
BASE_DIR = PathHelper(project_root)

if __name__ == '__main__':
    # Enable High DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Desainia MS Tool")
    app.setOrganizationName("Desainia")
    app.setApplicationDisplayName("Desainia MS Tool")
    app.BASE_DIR = BASE_DIR  # Make available to entire application
    
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
