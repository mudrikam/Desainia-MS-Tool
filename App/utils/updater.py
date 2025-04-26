import requests
import semver
import tempfile
import os
import shutil
import subprocess
import json
import platform
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
            config_path = os.path.join(os.getcwd(), "App", "config", "config.json")
            
            # Create platform-specific update script
            if platform.system() == "Windows":
                update_script = f"""
@echo off
timeout /t 1 /nobreak >nul
robocopy "{extracted_dir}" "{os.getcwd()}" /E /IS /IT /IM
if exist "{config_path.replace('/', '\\')}" (
    python -c "import json;fp='{config_path.replace('\\', '\\\\')}';f=open(fp,'r');d=json.load(f);f.close();d['application']['version']='{new_version}';f=open(fp,'w');json.dump(d,f,indent=4);f.close()"
    if errorlevel 1 (
        exit /b 1
    )
)
start "" "{os.getcwd().replace('/', '\\\\')}\\\\Launcher.bat"
rmdir /S /Q "{temp_dir.replace('/', '\\')}"
del "%~f0"
exit
"""
                script_path = os.path.join(temp_dir, "update.bat")
            else:  # Linux and MacOS
                if platform.system() == "Darwin":  # macOS
                    launch_cmd = f'open "{os.getcwd()}/Launcher.command"'
                    mac_launcher = f"""#!/bin/bash
cp -R "{extracted_dir}/"* "{os.getcwd()}/"
if [ -f "{config_path}" ]; then
    python3 -c 'import json;fp="{config_path}";f=open(fp,"r");d=json.load(f);f.close();d["application"]["version"]="{new_version}";f=open(fp,"w");json.dump(d,f,indent=4);f.close()'
fi
rm -rf "{temp_dir}"
if [ -f "{os.getcwd()}/Launcher.command" ]; then
    chmod +x "{os.getcwd()}/Launcher.command"
    {launch_cmd}
fi
rm -- "$0"
"""
                    update_script = mac_launcher
                else:  # Linux
                    launch_cmd = f'nohup "{os.getcwd()}/Launcher.sh" >/dev/null 2>&1 &'
                    update_script = f"""#!/bin/bash
cp -R "{extracted_dir}/"* "{os.getcwd()}/"
if [ -f "{config_path}" ]; then
    python3 -c 'import json;fp="{config_path}";f=open(fp,"r");d=json.load(f);f.close();d["application"]["version"]="{new_version}";f=open(fp,"w");json.dump(d,f,indent=4);f.close()'
fi
rm -rf "{temp_dir}"
if [ -f "{os.getcwd()}/Launcher.sh" ]; then
    chmod +x "{os.getcwd()}/Launcher.sh"
    {launch_cmd}
fi
rm -- "$0"
"""
                script_path = os.path.join(temp_dir, "update.sh")
            
            # Write and execute update script
            with open(script_path, 'w', newline='\n') as f:
                f.write(update_script)
            
            if platform.system() != "Windows":
                os.chmod(script_path, 0o755)  # Make script executable on Unix
            
            dialog.progress.setValue(75)
            dialog.status_label.setText("Installing update...")
            
            # Run update script
            if platform.system() == "Windows":
                subprocess.Popen([script_path], shell=True)
            else:
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
