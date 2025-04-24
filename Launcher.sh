#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        PYTHON_DIR="Python/Linux"
        # Pre-load XCB libraries
        export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
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

# Set complete environment
PYTHON_ROOT="${PWD}/${PYTHON_DIR}/python"
SITE_PACKAGES="${PYTHON_ROOT}/lib/python3.12/site-packages"

export PYTHONHOME="${PYTHON_ROOT}"
export PYTHONPATH="${SITE_PACKAGES}:${PYTHON_ROOT}/lib"
export LD_LIBRARY_PATH="${PYTHON_ROOT}/lib:${SITE_PACKAGES}/PyQt6/Qt6/lib:${LD_LIBRARY_PATH}"
export PATH="${PYTHON_ROOT}/bin:${PATH}"

# Set complete Qt environment
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export QT_PLUGIN_PATH="${SITE_PACKAGES}/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_PLUGIN_PATH}/platforms"

# Run with proper environment
"${PYTHON_ROOT}/bin/python3" Launcher.py
