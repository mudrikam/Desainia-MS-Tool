#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        PYTHON_DIR="Python/Linux"
        ;;
    Darwin*)
        PYTHON_DIR="Python/MacOS"
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Check if Python venv exists
if [ ! -d "${PYTHON_DIR}/venv" ]; then
    echo "Python environment not found. Running installer..."
    chmod +x Install.sh
    ./Install.sh
    if [ $? -ne 0 ]; then
        echo "Installation failed."
        exit 1
    fi
fi

# Activate virtual environment and run
source "${PYTHON_DIR}/venv/bin/activate"
python3 Launcher.py
