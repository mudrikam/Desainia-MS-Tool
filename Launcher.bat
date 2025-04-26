@echo off
setlocal enabledelayedexpansion

:: Check if Python exists in Windows folder
if not exist "Python\Windows\python.exe" (
    echo Python not found. Running installer...
    call Install.bat || (
        echo Installation failed.
        exit /b 1
    )
)

:: Check required packages
echo Checking components...
if exist "requirements.txt" (
    for /f "tokens=1 delims=<>= " %%G in (requirements.txt) do (
        if not "%%G" == "" if not "%%G:~0,1%" == "#" (
            Python\Windows\python.exe -c "import %%G" 2>nul
            if errorlevel 1 (
                echo Update needed. Installing components...
                call Install.bat
                goto :set_env
            )
        )
    )
)

:set_env
:: Set environment
set PYTHONPATH=Python\Windows;Python\Windows\Lib\site-packages
set PATH=Python\Windows;Python\Windows\Scripts;%PATH%
set QT_PLUGIN_PATH=Python\Windows\Lib\site-packages\PyQt6\Qt6\plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=Python\Windows\Lib\site-packages\PyQt6\Qt6\plugins\platforms

:: Run the launcher
Python\Windows\python.exe main.py
