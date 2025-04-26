import requests
import semver
import tempfile
import os
import shutil
import subprocess
import json
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox
from ..gui.widgets.dialogs.update_dialog import UpdateDialog

class UpdateChecker(QThread):
    update_available = pyqtSignal(str)
    download_progress = pyqtSignal(int)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.api_url = "https://api.github.com/repos/mudrikam/Desainia-MS-Tool/releases/latest"
    
    def run(self):
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code == 200:
                latest = response.json()
                latest_version = latest['tag_name'].replace('v', '')  # Remove v prefix for semver compare
                
                if semver.compare(latest_version, self.current_version) > 0:
                    self.update_available.emit(latest_version)
        except:
            pass  # Silently fail on connection issues
    
    def download_and_install(self, new_version):
        dialog = UpdateDialog(self.current_version, new_version)
        dialog.update_btn.clicked.connect(lambda: self._perform_update(dialog, new_version))
        return dialog.exec()
    
    def _perform_update(self, dialog, new_version):
        try:
            dialog.progress.show()
            dialog.update_btn.setEnabled(False)
            dialog.status_label.setText("Downloading update...")
            
            # Download new version
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "update.zip")
            download_url = f"https://github.com/mudrikam/Desainia-MS-Tool/archive/refs/tags/v{new_version}.zip"
            
            response = requests.get(download_url, stream=True)
            if response.status_code != 200:
                raise Exception("Failed to download update package")
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            with open(temp_file, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for data in response.iter_content(chunk_size=4096):
                        downloaded += len(data)
                        f.write(data)
                        progress = int((downloaded / total_size) * 100)
                        dialog.progress.setValue(progress)
            
            # Extract update
            dialog.status_label.setText("Extracting update...")
            dialog.progress.setValue(0)
            import zipfile
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            dialog.progress.setValue(50)
            
            # Prepare update
            dialog.status_label.setText("Preparing to install...")
            extracted_dir = os.path.join(temp_dir, f"Desainia-MS-Tool-{new_version}")
            update_script = f"""
@echo off
timeout /t 1 /nobreak >nul
robocopy "{extracted_dir}" "{os.getcwd()}" /E /IS /IT /IM
if exist "{os.getcwd()}\\App\\config\\config.json" (
    echo {{\"application\": {{\"version\": \"{new_version}\"}}, \"runtime\": {{\"python_version\": \"3.12.1\", \"qt_version\": \"6.6.1\"}}}} > "{os.getcwd()}\\App\\config\\config.json.new"
    move /Y "{os.getcwd()}\\App\\config\\config.json.new" "{os.getcwd()}\\App\\config\\config.json"
)
start "" "{os.getcwd()}\\Launcher.bat"
rmdir /S /Q "{temp_dir}"
del "%~f0"
"""
            script_path = os.path.join(temp_dir, "update.bat")
            with open(script_path, 'w') as f:
                f.write(update_script)
            
            dialog.progress.setValue(75)
            dialog.status_label.setText("Installing update...")
            
            # Run update script
            subprocess.Popen([script_path], shell=True)
            dialog.progress.setValue(100)
            dialog.status_label.setText("Update complete! Restarting...")
            
            # Wait briefly before closing
            QThread.msleep(1500)
            QApplication.instance().quit()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Update Error", f"Failed to update: {str(e)}")
            dialog.update_btn.setEnabled(True)
            dialog.progress.hide()
