@echo off
setlocal enabledelayedexpansion

:: Create Python directory if not exists
if not exist "Python\Windows" mkdir Python\Windows

:: Download Python 3.12 portable instead of 3.14
echo Downloading Python 3.12 portable...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.1/python-3.12.1-embed-amd64.zip' -OutFile 'Python\Windows\python.zip'}"

:: Extract Python
echo Extracting Python...
powershell -Command "& {Expand-Archive -Path 'Python\Windows\python.zip' -DestinationPath 'Python\Windows' -Force}"
del /f /q "Python\Windows\python.zip"

:: Create python._pth file with correct version
echo Creating python._pth file...
(
echo python312.zip
echo .
echo Lib/site-packages
) > "Python\Windows\python312._pth"

:: Create Scripts and Lib directories
mkdir "Python\Windows\Scripts" 2>nul
mkdir "Python\Windows\Lib\site-packages" 2>nul

:: Download get-pip.py
echo Downloading pip installer...
powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'Python\Windows\get-pip.py'}"

:: Set PYTHONPATH and PATH
set PYTHONPATH=Python\Windows;Python\Windows\Lib\site-packages
set PATH=Python\Windows;Python\Windows\Scripts;%PATH%

:: Install pip and essential tools
echo Installing pip...
.\Python\Windows\python.exe "Python\Windows\get-pip.py" --no-warn-script-location
del /f /q "Python\Windows\get-pip.py"
Python\Windows\python.exe -m pip install --no-warn-script-location wheel

:: Install requirements (pre-built wheels only)
echo Installing requirements...
Python\Windows\python.exe -m pip install --no-warn-script-location --only-binary :all: -r requirements.txt
if errorlevel 1 (
    echo Error: Could not install pre-built packages.
    echo Please check your internet connection or try a different Python version.
    pause
    exit /b 1
)

:: Ensure Qt6 DLLs are accessible
set QT_PLUGIN_PATH=Python\Windows\Lib\site-packages\PyQt6\Qt6\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=Python\Windows\Lib\site-packages\PyQt6\Qt6\plugins\platforms

echo Installation completed successfully!
pause
