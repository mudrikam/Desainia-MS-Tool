#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        PYTHON_DIR="Python/Linux"
        # Set Linux-specific vars
        export XDG_RUNTIME_DIR="/run/user/$(id -u)"
        export QT_QPA_PLATFORM=xcb
        # System libraries path
        export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib:${LD_LIBRARY_PATH}"
        ;;
    Darwin*)
        PYTHON_DIR="Python/MacOS"
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Check Python installation
if [ ! -f "${PYTHON_DIR}/python/bin/python3.12" ]; then
    echo "Python not found. Running installer..."
    chmod +x Install.sh
    ./Install.sh
    if [ $? -ne 0 ]; then
        echo "Installation failed."
        exit 1
    fi
fi

# Check required packages
echo "Checking components..."
NEEDS_INSTALL=0
if [ -f "requirements.txt" ]; then
    while IFS= read -r package || [ -n "$package" ]; do
        if [[ $package =~ ^[^#] ]]; then
            packagename=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | tr -d ' ')
            if ! "${PYTHON_DIR}/python/bin/python3.12" -c "import ${packagename}" 2>/dev/null; then
                echo "Update needed. Installing components..."
                NEEDS_INSTALL=1
                break
            fi
        fi
    done < requirements.txt

    if [ $NEEDS_INSTALL -eq 1 ]; then
        chmod +x Install.sh
        ./Install.sh
        if [ $? -ne 0 ]; then
            echo "Installation failed."
            exit 1
        fi
    fi
fi

# Set environment
PYTHON_ROOT="${PWD}/${PYTHON_DIR}/python"
export PYTHONHOME="${PYTHON_ROOT}"
export PYTHONPATH="${PYTHON_ROOT}/lib/python3.12/site-packages:${PYTHON_ROOT}/lib/python3.12"
export PATH="${PYTHON_ROOT}/bin:${PATH}"
unset QT_DEBUG_PLUGINS
export QT_PLUGIN_PATH="${PYTHON_ROOT}/lib/python3.12/site-packages/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_PLUGIN_PATH}/platforms"

# Run application
exec "${PYTHON_ROOT}/bin/python3.12" main.py 2>/dev/null
