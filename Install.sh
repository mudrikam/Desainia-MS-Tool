#!/bin/bash

# Determine OS and Python version
OS="$(uname -s)"
PYTHON_VERSION="3.12.1"

case "${OS}" in
    Linux*)
        INSTALL_DIR="Python/Linux"
        PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz"
        echo "Installing on Linux..."
        ;;
    Darwin*)
        INSTALL_DIR="Python/MacOS"
        PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}-macos11.pkg"
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

# Download Python
echo "Downloading Python ${PYTHON_VERSION}..."
curl -o python.tgz "${PYTHON_URL}"

# Extract Python
echo "Extracting Python..."
tar xzf python.tgz
rm python.tgz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Set up pip
echo "Installing pip..."
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py --no-warn-script-location
rm get-pip.py

# Install wheel
pip install --no-warn-script-location wheel

# Install requirements
echo "Installing requirements..."
cd ../..  # Back to project root
if [ -f "requirements.txt" ]; then
    pip install --no-warn-script-location --only-binary :all: -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing requirements. Please check your internet connection."
        exit 1
    fi
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Set up Qt paths
export QT_PLUGIN_PATH="${INSTALL_DIR}/venv/lib/python3.12/site-packages/PyQt6/Qt6/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${INSTALL_DIR}/venv/lib/python3.12/site-packages/PyQt6/Qt6/plugins/platforms"

echo "Installation completed successfully!"
