#!/bin/bash

# Determine OS and version
OS="$(uname -s)"
PYTHON_VERSION="3.12.10"
RELEASE_TAG="20250409"

case "${OS}" in
    Linux*)
        INSTALL_DIR="Python/Linux"
        # Check and install required Qt dependencies
        echo "Checking Qt dependencies..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y libxcb-cursor0 libxcb-xinerama0 libxcb-randr0 libxcb-xtest0 libxcb-shape0 libxcb-cursor0
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y libxcb xcb-util-cursor
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm xcb-util-cursor
        else
            echo "Warning: Could not install Qt dependencies automatically. Please install xcb-cursor0 manually."
        fi
        PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE_TAG}/cpython-${PYTHON_VERSION}+${RELEASE_TAG}-x86_64-unknown-linux-gnu-install_only.tar.gz"
        echo "Installing on Linux..."
        ;;
    Darwin*)
        INSTALL_DIR="Python/MacOS"
        PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE_TAG}/cpython-${PYTHON_VERSION}+${RELEASE_TAG}-x86_64-apple-darwin-install_only.tar.gz"
        echo "Installing on macOS..."
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Create directory
mkdir -p "${INSTALL_DIR}"
cd "${INSTALL_DIR}"

# Download Python build
echo "Downloading Python ${PYTHON_VERSION}..."
curl -L -o python.tar.gz "${PYTHON_URL}"

# Extract Python with verbose output for debugging
echo "Extracting Python..."
tar xvf python.tar.gz
rm python.tar.gz

# Create additional directories if needed
mkdir -p lib/site-packages

# Set up environment
export PATH="${PWD}/python/bin:${PATH}"  # Fixed path to match actual structure
export PYTHONPATH="${PWD}/python/lib:${PWD}/lib/site-packages"

# Install requirements
echo "Installing requirements..."
cd ../..  # Back to project root
if [ -f "requirements.txt" ]; then
    ./Python/${OS}/python/bin/python3 -m pip install --no-warn-script-location -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing requirements. Please check your internet connection."
        exit 1
    fi
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Set up Qt paths - updated to match actual structure
export QT_PLUGIN_PATH="${INSTALL_DIR}/python/lib/site-packages/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${INSTALL_DIR}/python/lib/site-packages/PyQt6/Qt6/plugins/platforms"

echo "Installation completed successfully!"
