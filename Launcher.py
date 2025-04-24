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

# This launcher initializes and runs the Desainia-MS-Tool application
# by creating an instance of MainWindow class from App.window module

import os
import sys
import platform

def verify_python_installation():
    """Verify Python installation exists for current platform"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if platform.system() == "Windows":
        python_exe = os.path.join(base_dir, "Python", "Windows", "python.exe")
        if not os.path.exists(python_exe):
            raise RuntimeError("Python installation not found. Please run Install.bat")
    else:  # Linux/MacOS
        venv_dir = os.path.join(
            base_dir, 
            "Python",
            "Linux" if platform.system() == "Linux" else "MacOS",
            "venv"
        )
        if not os.path.exists(venv_dir):
            raise RuntimeError("Python virtual environment not found. Please run Install.sh")

def setup_python_path():
    """Configure Python path based on platform"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add application root directory to path
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    
    if platform.system() == "Windows":
        python_dir = os.path.join(base_dir, "Python", "Windows")
        lib_dir = os.path.join(python_dir, "Lib", "site-packages")
    else:  # Linux/MacOS
        platform_dir = "Linux" if platform.system() == "Linux" else "MacOS"
        python_dir = os.path.join(base_dir, "Python", platform_dir, "venv")
        lib_dir = os.path.join(python_dir, "lib", "python3.14", "site-packages")

    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)

# Verify and setup Python before importing application modules
verify_python_installation()
setup_python_path()

from App.window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()
