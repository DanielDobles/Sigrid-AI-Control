#!/usr/bin/env python3
"""
SIGRID Desktop Application Launcher
Quick launcher script for the desktop application
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Launch desktop application
from src.ui.desktop_app import main

if __name__ == "__main__":
    main()
