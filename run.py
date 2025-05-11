#!/usr/bin/env python
"""
Runner script for the Teck Resources Commodity Price Dashboard.
Launches the Streamlit application.
"""

import os
import sys
import subprocess
import logging
import argparse

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
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Run the Commodity Price Dashboard')
        parser.add_argument('--cloud', action='store_true', help='Use Cloud-optimized version')
        args = parser.parse_args()

        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        if args.cloud:
            # Use the cloud-optimized version for Streamlit Cloud
            main_path = os.path.join(script_dir, "streamlit_deploy", "streamlit_app.py")
            logger.info("Using cloud-optimized version for Streamlit Cloud")
        else:
            # Use the standard version for local development
            main_path = os.path.join(script_dir, "src", "main.py")

        logger.info(f"Starting Streamlit with: {main_path}")

        # Run Streamlit
        result = subprocess.run(
            ["streamlit", "run", main_path],
            check=True,
            text=True
        )

        return result.returncode

    except Exception as e:
        logger.error(f"Error running dashboard: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())