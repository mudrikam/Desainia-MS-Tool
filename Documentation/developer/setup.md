# Development Setup Guide

## Prerequisites

- Python 3.8 or higher
- Git
- Your favorite IDE/editor
- Knowledge of PyQt6

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/mudrikam/Desainia-MS-Tool.git
cd Desainia-MS-Tool
```

2. Install dependencies:
```bash
# Windows
Launcher.bat

# macOS/Linux
./Launcher.sh
```

3. Set up development environment:
```bash
# Optional: Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

## Project Structure

```
Desainia-MS-Tool/
├── App/                    # Main application code
│   ├── core/              # Business logic
│   ├── gui/               # User interface
│   └── utils/             # Utilities
├── documentation/         # Documentation
└── tests/                # Unit tests
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Run tests
4. Submit pull request

See [Contributing Guide](contributing.md) for more details.
