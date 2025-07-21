#!/usr/bin/env python3
"""
Azure AI DevOps Agent - Main Application Entry Point
Run: streamlit run app.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main Streamlit app
from ui.enhanced_streamlit_app import main

if __name__ == "__main__":
    main()