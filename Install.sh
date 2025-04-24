#!/bin/bash

# Determine OS
OS="$(uname -s)"
PYTHON_VERSION="3.14.0"

case "${OS}" in
    Linux*)
        INSTALL_DIR="Python/Linux"
        echo "Installing on Linux..."
        mkdir -p "${INSTALL_DIR}"
        # Check for package manager
        if command -v apt-get >/dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3.14 python3-pip
        elif command -v dnf >/dev/null; then
            sudo dnf install -y python3.14 python3-pip
        elif command -v pacman >/dev/null; then
            sudo pacman -Sy python314 python-pip
        else
            echo "Unsupported package manager. Please install Python 3.14+ manually."
            exit 1
        fi
        python3 -m venv "${INSTALL_DIR}/venv"
        source "${INSTALL_DIR}/venv/bin/activate"
        ;;
    Darwin*)
        INSTALL_DIR="Python/MacOS"
        echo "Installing on macOS..."
        mkdir -p "${INSTALL_DIR}"
        # Check if Homebrew is installed
        if ! command -v brew >/dev/null; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python@3.14
        python3 -m venv "${INSTALL_DIR}/venv"
        source "${INSTALL_DIR}/venv/bin/activate"
        ;;
    *)
        echo "Unsupported operating system"
        exit 1
        ;;
esac

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install --no-warn-script-location -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing requirements. Please check your internet connection."
        exit 1
    fi
else
    echo "Error: requirements.txt not found."
    exit 1
fi

echo "Installation completed successfully!"
