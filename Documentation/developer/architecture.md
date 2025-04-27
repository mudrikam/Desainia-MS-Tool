# Architecture Overview

## Component Architecture

```
+----------------+     +----------------+     +----------------+
|     GUI        |     |     Core       |     |     Utils      |
|  PyQt6-based   |---->|   Business     |---->|   Helper       |
|  Components    |     |    Logic       |     |   Functions    |
+----------------+     +----------------+     +----------------+
         |                    |                     |
         v                    v                     v
+----------------+     +----------------+     +----------------+
|    Config      |     |      API       |     |    Storage     |
|  Settings &    |     |    External    |     |     File &     |
| Translations   |     |    Services    |     |     Cache      |
+----------------+     +----------------+     +----------------+
```

## Key Components

### GUI Layer
- Window management
- User interface components
- Event handling

### Core Layer
- Business logic
- Data processing
- Upload management

### Utils Layer
- Helper functions
- Common utilities
- Support services

## Data Flow

1. User interacts with GUI
2. GUI triggers Core functions
3. Core processes data using Utils
4. Results displayed via GUI

## Technology Stack

- Python 3.8+
- PyQt6
- Pillow
- Requests

For detailed implementation, see source code documentation.
