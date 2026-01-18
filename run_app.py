#!/usr/bin/env python3
"""
Launcher script for the Agentic Search Streamlit application.
This script properly sets up the Python path for relative imports.
"""

import os
import sys
import subprocess

# Add the current directory to Python path so relative imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Run streamlit from the project root with proper path setup
env = os.environ.copy()
env['PYTHONPATH'] = current_dir

# Use streamlit run with the module path
subprocess.run(['streamlit', 'run', 'agentic_search/app.py'], env=env)