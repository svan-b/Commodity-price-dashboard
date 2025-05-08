#!/usr/bin/env python3
"""
Runner script for the Teck Resources Commodity Price Dashboard.
Launches the Streamlit application directly without a virtual environment.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Run the Streamlit dashboard application.
    """
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the main.py file
        main_path = os.path.join(script_dir, "src", "main.py")
        
        logger.info(f"Starting Streamlit with: {main_path}")
        
        # Run Streamlit
        cmd = ["streamlit", "run", main_path]
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Use the system Python to run Streamlit
        result = subprocess.run(
            cmd,
            check=True,
            text=True
        )
        
        return result.returncode
        
    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())