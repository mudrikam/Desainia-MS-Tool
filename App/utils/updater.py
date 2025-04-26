import requests
import semver
import tempfile
import os
import shutil
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
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
                latest_version = latest['tag_name'].lstrip('v')
                
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
            
            # Get download URL from release
            response = requests.get(self.api_url)
            release = response.json()
            download_url = release['assets'][0]['browser_download_url']
            
            # Download new version
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "update.zip")
            
            response = requests.get(download_url, stream=True)
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
            
            # Create update script
            script_content = f"""
@echo off
timeout /t 1 /nobreak >nul
xcopy /E /I /Y "{temp_file}" "{os.getcwd()}"
start "" "{os.getcwd()}\\Launcher.bat"
del "%~f0"
            """
            
            script_path = os.path.join(temp_dir, "update.bat")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute update script and close application
            subprocess.Popen([script_path], shell=True)
            QApplication.instance().quit()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(dialog, "Update Error", f"Failed to update: {str(e)}")
            dialog.update_btn.setEnabled(True)
            dialog.progress.hide()
