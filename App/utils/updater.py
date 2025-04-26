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
    update_available = pyqtSignal(str, str)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.api_url = "https://api.github.com/repos/mudrikam/Desainia-MS-Tool/releases/latest"
        self.commit_url = "https://api.github.com/repos/mudrikam/Desainia-MS-Tool/commits/"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'Desainia-MS-Tool/{current_version}'  # Menggunakan versi aplikasi di User-Agent
        }
        self.latest_version = None
        self.release_notes = None
        self.commit_hash = None
    
    def run(self):
        try:
            # Add error handling for rate limiting
            response = requests.get(self.api_url, headers=self.headers, timeout=5)
            print(f"GitHub API Response: {response.status_code}")
            
            if response.status_code == 403:
                print("Rate limit exceeded, waiting before retry...")
                return
                
            if response.status_code == 200:
                latest = response.json()
                self.latest_version = latest['tag_name'].replace('v', '')  # Remove v prefix for semver compare
                self.release_notes = latest.get('body', 'No release notes available.')
                
                # Get commit hash for current tag
                tag_commit_url = f"https://api.github.com/repos/mudrikam/Desainia-MS-Tool/git/refs/tags/v{self.current_version}"
                commit_response = requests.get(tag_commit_url, headers=self.headers, timeout=5)
                if commit_response.status_code == 200:
                    commit_data = commit_response.json()
                    self.commit_hash = commit_data['object']['sha'][:7]  # Get short hash
                    
                    # Update config with commit hash
                    try:
                        app = QApplication.instance()
                        config_path = app.BASE_DIR.get_path('App', 'config', 'config.json')
                        with open(config_path, 'r+') as f:
                            config = json.load(f)
                            if 'git' not in config:
                                config['git'] = {}
                            config['git']['commit_hash'] = self.commit_hash
                            config['git']['tag'] = f"v{self.current_version}"
                            f.seek(0)
                            json.dump(config, f, indent=4)
                            f.truncate()
                    except Exception as e:
                        print(f"Error updating config with commit hash: {str(e)}")
                
                if semver.compare(self.latest_version, self.current_version) > 0:
                    print(f"Update available: {self.latest_version}")
                    self.update_available.emit(self.latest_version, self.release_notes)
        except Exception as e:
            print(f"Update check error: {str(e)}")
            pass

    def download_and_install(self, new_version):
        if not self.release_notes:  # Fallback if release notes not available
            self.release_notes = 'No release notes available.'
        dialog = UpdateDialog(self.current_version, new_version, self.release_notes)
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
            
            # Get new commit hash
            tag_commit_url = f"https://api.github.com/repos/mudrikam/Desainia-MS-Tool/git/refs/tags/v{new_version}"
            commit_response = requests.get(tag_commit_url, headers=self.headers, timeout=5)
            new_commit_hash = ""
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                new_commit_hash = commit_data['object']['sha'][:7]
            
            # Create platform-specific update script
            if platform.system() == "Windows":
                update_script = f"""
@echo off
timeout /t 1 /nobreak >nul
robocopy "{extracted_dir}" "{os.getcwd()}" /E /IS /IT /IM
if exist "{config_path.replace('/', '\\')}" (
    python -c "import json;fp='{config_path.replace('\\', '\\\\')}';f=open(fp,'r');d=json.load(f);f.close();d['application']['version']='{new_version}';d['git']={{'commit_hash':'{new_commit_hash}','tag':'v{new_version}'}};f=open(fp,'w');json.dump(d,f,indent=4);f.close()"
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
                update_script = f"""#!/bin/bash
cp -R "{extracted_dir}/"* "{os.getcwd()}/"

if [ -f "{config_path}" ]; then
    python3 -c 'import json;fp="{config_path}";f=open(fp,"r");d=json.load(f);f.close();d["application"]["version"]="{new_version}";d["git"]={{"commit_hash":"{new_commit_hash}","tag":"v{new_version}"}};f=open(fp,"w");json.dump(d,f,indent=4);f.close()'
fi

if [ -f "{os.getcwd()}/Launcher.sh" ]; then
    chmod +x "{os.getcwd()}/Launcher.sh"
    nohup bash "{os.getcwd()}/Launcher.sh" > /dev/null 2>&1 &
fi

rm -rf "{temp_dir}"
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
