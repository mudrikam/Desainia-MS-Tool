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

# Check if Python exists
if [ ! -f "${PYTHON_DIR}/python/bin/python3" ]; then
    echo "Python not found. Running installer..."
    chmod +x Install.sh
    ./Install.sh
    if [ $? -ne 0 ]; then
        echo "Installation failed."
        exit 1
    fi
fi

# Set Python paths
export PYTHONPATH="${PYTHON_DIR}/python/lib:${PYTHON_DIR}/lib/site-packages"
export PATH="${PYTHON_DIR}/python/bin:${PATH}"

# Set Qt paths
export QT_PLUGIN_PATH="${PYTHON_DIR}/python/lib/site-packages/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${PYTHON_DIR}/python/lib/site-packages/PyQt6/Qt6/plugins/platforms"

# Run the launcher
./${PYTHON_DIR}/python/bin/python3 Launcher.py
