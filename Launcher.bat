@echo off
setlocal enabledelayedexpansion

:: Check if Python exists in Windows folder
if not exist "Python\Windows\python.exe" (
    echo Python not found. Running installer...
    call Install.bat
    if errorlevel 1 (
        echo Installation failed.
        pause
        exit /b 1
    )
)

:: Set Python paths
set PYTHONPATH=Python\Windows;Python\Windows\Lib\site-packages
set PATH=Python\Windows;Python\Windows\Scripts;%PATH%

:: Set Qt paths
set QT_PLUGIN_PATH=Python\Windows\Lib\site-packages\PyQt6\Qt6\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=Python\Windows\Lib\site-packages\PyQt6\Qt6\plugins\platforms

:: Run the launcher
Python\Windows\python.exe Launcher.py
