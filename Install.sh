#!/bin/bash

# Determine OS and version
OS="$(uname -s)"
PYTHON_VERSION="3.12.10"
RELEASE_TAG="20250409"

case "${OS}" in
    Linux*)
        OS_DIR="Linux"
        INSTALL_DIR="Python/${OS_DIR}"
        # Quietly check and install system requirements
        if command -v apt-get &> /dev/null; then
            if ! dpkg -s libxcb1 >/dev/null 2>&1; then
                echo "Installing system requirements..."
                sudo apt-get update >/dev/null 2>&1
                sudo apt-get install -y libxcb1 libxcb-cursor0 libxcb-xinerama0 \
                    libxcb-randr0 libxcb-keysyms1 libxkbcommon-x11-0 >/dev/null 2>&1
            fi
        elif command -v dnf &> /dev/null; then
            if ! rpm -q libxcb >/dev/null 2>&1; then
                echo "Installing system requirements..."
                sudo dnf install -y libxcb xcb-util-cursor libxkbcommon-x11 >/dev/null 2>&1
            fi
        elif command -v pacman &> /dev/null; then
            if ! pacman -Q xcb-util-cursor >/dev/null 2>&1; then
                echo "Installing system requirements..."
                sudo pacman -Sy --noconfirm xcb-util-cursor libxkbcommon-x11 >/dev/null 2>&1
            fi
        fi
        echo "Preparing installation..."
        PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE_TAG}/cpython-${PYTHON_VERSION}+${RELEASE_TAG}-x86_64-unknown-linux-gnu-install_only.tar.gz"
        ;;
    Darwin*)
        OS_DIR="MacOS"    # Use MacOS for directory despite Darwin detection
        INSTALL_DIR="Python/${OS_DIR}"
        echo "Preparing installation..."
        PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE_TAG}/cpython-${PYTHON_VERSION}+${RELEASE_TAG}-x86_64-apple-darwin-install_only.tar.gz"
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Save base directory
BASE_DIR="$(pwd)"

# Check if Python and pip are already installed and working
if [ -f "${INSTALL_DIR}/python/bin/python3.12" ]; then
    "${INSTALL_DIR}/python/bin/python3.12" -m pip --version >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        # Check if all requirements are already installed
        NEEDS_INSTALL=0
        while IFS= read -r package || [ -n "$package" ]; do
            if [[ $package =~ ^[^#] ]]; then  # Skip comments
                packagename=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | tr -d ' ')
                if ! "${INSTALL_DIR}/python/bin/python3.12" -c "import ${packagename}" 2>/dev/null; then
                    NEEDS_INSTALL=1
                    break
                fi
            fi
        done < requirements.txt
        
        if [ $NEEDS_INSTALL -eq 0 ]; then
            echo "All components are up to date."
            exit 0
        fi
    fi
fi

# Installation steps
if [ ! -f "${INSTALL_DIR}/python/bin/python3.12" ]; then
    echo "Installing required components..."
    mkdir -p "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
    curl -L -o python.tar.gz "${PYTHON_URL}" 2>/dev/null
    tar xf python.tar.gz >/dev/null 2>&1
    rm python.tar.gz
    mkdir -p lib/site-packages
    cd "${BASE_DIR}"
fi

# Set up environment (using absolute paths)
export PATH="${BASE_DIR}/${INSTALL_DIR}/python/bin:${PATH}"
export PYTHONPATH="${BASE_DIR}/${INSTALL_DIR}/python/lib:${BASE_DIR}/${INSTALL_DIR}/lib/site-packages"

# Install requirements
if [ -f "${BASE_DIR}/requirements.txt" ]; then
    echo "Installing additional components..."
    echo "This may take a few minutes, please wait..."
    "${BASE_DIR}/Python/${OS_DIR}/python/bin/python3.12" -m pip install --no-cache-dir -r "${BASE_DIR}/requirements.txt"
    if [ $? -eq 0 ]; then
        echo
        echo "Installation completed successfully!"
    else
        echo
        echo "Installation failed. Please try:"
        echo "1. Check your internet connection"
        echo "2. Run Install.sh with sudo"
        echo "3. If still failing, try running manually:"
        echo "   ${BASE_DIR}/Python/${OS_DIR}/python/bin/python3.12 -m pip install --no-cache-dir -r requirements.txt"
        exit 1
    fi
else
    echo "Installation failed. Missing requirements.txt file."
    exit 1
fi

# Set up Qt paths (using absolute paths)
QT_BASE="${BASE_DIR}/Python/${OS_DIR}/python/lib/python3.12/site-packages/PyQt6/Qt6"
export QT_PLUGIN_PATH="${QT_BASE}/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_BASE}/plugins/platforms"
