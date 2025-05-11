"""
Main entry point for Streamlit Cloud deployment.
This file should be specified as the main file path in Streamlit Cloud.
"""

import os
import sys
import logging
import streamlit as st

# Configure logging to avoid excessive disk usage
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for full dashboard deployment.
    """
    try:
        logger.info("Starting Streamlit Cloud app - FULL PRODUCTION MODE")
        
        # Try to ensure directories exist
        try:
            from setup_cloud import ensure_directories
            ensure_directories()
        except Exception as setup_error:
            logger.warning(f"Error ensuring directories: {str(setup_error)}")
            
        # First try to run the simplified test app
        try:
            from streamlit_deploy.simple_app import main as simple_main
            simple_main()
            return
        except Exception as e1:
            logger.warning(f"Error running simplified app: {str(e1)}")
            
            # Fall back to simple error display
            st.set_page_config(page_title="Commodity Dashboard", page_icon="📊", layout="wide")
            st.title("Commodity Price Dashboard")
            
            st.error("Unable to initialize the application. Please try again later.")
            st.markdown("### Error Details")
            st.code(str(e1))
            
            # Show environment info
            st.markdown("### Environment Information")
            st.code(f"Python version: {sys.version}")
            st.code(f"Working directory: {os.getcwd()}")
            
            # List available directories
            try:
                dirs = os.listdir(".")
                st.code(f"Contents of current directory: {dirs}")
            except Exception as e2:
                st.warning(f"Could not list directory contents: {e2}")
            
    except Exception as e:
        # Last resort error display
        st.title("Commodity Price Dashboard - Error")
        st.error(f"Critical error: {str(e)}")

if __name__ == "__main__":
    main()