"""
Main entry point for Streamlit Cloud deployment.
This file is executed when the streamlit_deploy directory is run as a module.
"""

import os
import sys

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import and run the streamlit_cloud.py module
from streamlit_deploy.streamlit_cloud import main

if __name__ == "__main__":
    main()