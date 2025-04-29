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
echo Installing pip...
powershell -Command "& {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'Python\Windows\get-pip.py'}" >nul
if errorlevel 1 (
    echo Failed to download pip. Retrying...
    timeout /t 3 >nul
    powershell -Command "& {$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'Python\Windows\get-pip.py'}" >nul
)
set PYTHONPATH=Python\Windows;Python\Windows\Lib\site-packages
set PATH=Python\Windows;Python\Windows\Scripts;%PATH%
Python\Windows\python.exe "Python\Windows\get-pip.py" --no-warn-script-location >nul
del /f /q "Python\Windows\get-pip.py" >nul

:install_requirements
echo.
echo Installing additional components...
echo This may take a few minutes, please wait...
echo.

Python\Windows\python.exe -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo.
    echo Installation failed. Please try:
    echo 1. Check your internet connection
    echo 2. Run Install.bat as administrator
    echo 3. If still failing, try running manually:
    echo    Python\Windows\python.exe -m pip install --no-cache-dir -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Updating pip to latest version...
Python\Windows\python.exe -m pip install --upgrade pip

echo Installation completed successfully!
exit /b 0
