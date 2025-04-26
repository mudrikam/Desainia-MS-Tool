@echo off
setlocal enabledelayedexpansion

:: Check existing installation
if exist "Python\Windows\python.exe" (
    echo Checking existing installation...
    goto :install_requirements
)

:: Install Python
echo Installing required components...
if not exist "Python\Windows" mkdir Python\Windows
powershell -Command "& {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.1/python-3.12.1-embed-amd64.zip' -OutFile 'Python\Windows\python.zip'}" >nul
powershell -Command "& {Expand-Archive -Path 'Python\Windows\python.zip' -DestinationPath 'Python\Windows' -Force}" >nul
del /f /q "Python\Windows\python.zip" >nul

:: Setup Python environment
mkdir "Python\Windows\Scripts" 2>nul
mkdir "Python\Windows\Lib\site-packages" 2>nul
(
echo python312.zip
echo .
echo Lib/site-packages
) > "Python\Windows\python312._pth"

:: Install pip
powershell -Command "& {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'Python\Windows\get-pip.py'}" >nul
set PYTHONPATH=Python\Windows;Python\Windows\Lib\site-packages
set PATH=Python\Windows;Python\Windows\Scripts;%PATH%
Python\Windows\python.exe "Python\Windows\get-pip.py" --no-warn-script-location >nul
del /f /q "Python\Windows\get-pip.py" >nul

:install_requirements
echo Installing additional components...
Python\Windows\python.exe -m pip install --no-warn-script-location --only-binary :all: -r requirements.txt >nul
if errorlevel 1 (
    echo Installation failed. Please check your internet connection.
    exit /b 1
)

echo Installation completed successfully!
exit /b 0
