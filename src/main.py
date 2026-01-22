#!/usr/bin/env python3
"""
Main entry point for Cisco 4321 ISR Password Reset Tool
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import and run bootstrap
from bootstrap import main

if __name__ == "__main__":
    main()
