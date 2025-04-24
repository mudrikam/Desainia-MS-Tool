#!/bin/bash

# Determine OS and Python version
OS="$(uname -s)"
PYTHON_VERSION="3.12.1"

case "${OS}" in
    Linux*)
        INSTALL_DIR="Python/Linux"
        # Use standalone build instead of source
        PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}-amd64.tar.xz"
        echo "Installing on Linux..."
        ;;
    Darwin*)
        INSTALL_DIR="Python/MacOS"
        PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-macos11.pkg"
        echo "Installing on macOS..."
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Create directories
mkdir -p "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}/lib/site-packages"
cd "${INSTALL_DIR}"

# Download Python
echo "Downloading Python ${PYTHON_VERSION}..."
curl -L -o python.tar.xz "${PYTHON_URL}"

# Extract Python
echo "Extracting Python..."
tar xf python.tar.xz
rm python.tar.xz

# Set up environment
export PYTHONPATH="${PWD}:${PWD}/lib/site-packages"
export PATH="${PWD}/bin:${PATH}"

# Download and install pip
echo "Installing pip..."
curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
./bin/python3 get-pip.py --no-warn-script-location
rm get-pip.py

# Install wheel first
./bin/pip3 install --no-warn-script-location wheel

# Install requirements
echo "Installing requirements..."
cd ../..  # Back to project root
if [ -f "requirements.txt" ]; then
    ./Python/${OS}/bin/pip3 install --no-warn-script-location --only-binary :all: -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing requirements. Please check your internet connection."
        exit 1
    fi
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Set up Qt paths
export QT_PLUGIN_PATH="${INSTALL_DIR}/lib/python3.12/site-packages/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${INSTALL_DIR}/lib/python3.12/site-packages/PyQt6/Qt6/plugins/platforms"

echo "Installation completed successfully!"
