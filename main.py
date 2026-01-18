#!/usr/bin/env python3
"""
Streamlit entry point for the Agentic Search application.
This file sets up the proper package path and imports the main app.
"""

import sys
import os

# Add the current directory to the path so we can import agentic_search
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run the main app
from agentic_search.app import main

if __name__ == "__main__":
    main()