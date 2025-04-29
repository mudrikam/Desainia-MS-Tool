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
    show_update_dialog = pyqtSignal(str, str, str)  # Add new signal
    
    def __init__(self, current_version):
        try:
            super().__init__()
            self.current_version = current_version.strip()
            self.app = QApplication.instance()
            
            # Load config
            self.config_path = self.app.BASE_DIR.get_path('App', 'config', 'config.json')
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            # Get GitHub config and setup API
            github_config = self.config['repository']['github']
            self.api_url = f"{github_config['releases']}/latest"
            self.github_token = github_config.get('token', '')
            
            # Setup headers - token optional
            self.headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': self.config['application']['name'].replace(' ', '-')
            }
            if self.github_token:
                self.headers['Authorization'] = f'Bearer {self.github_token}'
            
            self.latest_version = None
            self.release_notes = None
            self.commit_hash = None

            self.show_update_dialog.connect(self._show_dialog)
            
        except Exception as e:
            print(f"Error in UpdateChecker initialization: {str(e)}")
            raise

    def _show_dialog(self, current_version, new_version, release_notes):
        if QApplication.instance().activeWindow():
            dialog = UpdateDialog(current_version, new_version, release_notes, QApplication.instance().activeWindow())
        else:
            dialog = UpdateDialog(current_version, new_version, release_notes)
        dialog.update_btn.clicked.connect(lambda: self._perform_update(dialog, new_version))
        dialog.show()

    def run(self):
        try:
            # Get commit hash for current version first
            tag_commit_url = f"{self.config['repository']['github']['api_base']}/git/refs/tags/v{self.current_version}"
            commit_response = requests.get(tag_commit_url, headers=self.headers, timeout=5)
            if commit_response.status_code == 401:
                self.headers.pop('Authorization', None)
                commit_response = requests.get(tag_commit_url, headers=self.headers, timeout=5)
                
            if commit_response.status_code == 200:
                commit_data = commit_response.json()
                current_commit_hash = commit_data['object']['sha'][:7]
                
                # Update config with current version's commit hash
                if 'git' not in self.config:
                    self.config['git'] = {}
                self.config['git'].update({
                    'commit_hash': current_commit_hash,
                    'tag': f"v{self.current_version}"
                })
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=4)

            # Then check for updates
            response = requests.get(self.api_url, headers=self.headers, timeout=5)
            
            if response.status_code != 200:
                if response.status_code in [401, 403]:
                    # Try without token if auth fails
                    self.headers.pop('Authorization', None)
                    response = requests.get(self.api_url, headers=self.headers, timeout=5)
                
                if response.status_code != 200:  # Still failed
                    print(f"Update check failed with status {response.status_code}")
                    return
            
            if response.status_code == 200:
                latest = response.json()
                if not latest:
                    return
                    
                self.latest_version = latest['tag_name'].replace('v', '').strip()
                
                # Check if this version should be skipped - from user preferences
                prefs_path = self.app.BASE_DIR.get_path('UserData', 'user_preferences.json')
                with open(prefs_path, 'r') as f:
                    user_prefs = json.load(f)
                
                skip_update = user_prefs.get('update', {}).get('skip_update', False)
                skip_version = user_prefs.get('update', {}).get('skip_version')
                
                if skip_update and skip_version == self.latest_version:
                    return
                    
                self.release_notes = latest.get('body', 'No release notes available.')
                
                # Update config
                if 'git' not in self.config:
                    self.config['git'] = {}
                self.config['git']['last_github_version'] = self.latest_version
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=4)
                
                try:
                    if semver.compare(self.latest_version, self.current_version) > 0:
                        self.update_available.emit(self.latest_version, self.release_notes)
                        self.show_update_dialog.emit(self.current_version, self.latest_version, self.release_notes)
                except Exception as ve:
                    print(f"Version comparison error: {str(ve)}")
                    
        except Exception as e:
            print(f"Update check error: {str(e)}")

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
            repo_url = self.config['repository']['github']['api_base'].replace('api.github.com/repos', 'github.com')
            download_url = f"{repo_url}/archive/refs/tags/v{new_version}.zip"
            
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
            extracted_dir = os.path.join(temp_dir, f"Desainia-Rak-Arsip-{new_version}")
            config_path = os.path.join(os.getcwd(), "App", "config", "config.json")
            
            # Get new commit hash
            tag_commit_url = f"{self.config['repository']['github']['api_base']}/git/refs/tags/v{new_version}"
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
