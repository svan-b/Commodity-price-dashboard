"""
Main entry point for Streamlit Cloud deployment.
This is a simple wrapper for the standalone app.
"""

import os
import sys
import logging
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import the standalone app
logger.info("Importing standalone app...")
try:
    # First try importing directly from current location
    # This is the path structure on Streamlit Cloud
    import app_standalone
    
    logger.info("Running app_standalone via direct import")
    app_standalone.main()
except ImportError as e:
    logger.warning(f"Error importing app_standalone directly: {str(e)}")
    
    try:
        # Try relative import from streamlit_deploy (local development)
        from streamlit_deploy import app_standalone
        
        logger.info("Running app_standalone via package import")
        app_standalone.main()
    except ImportError as e2:
        logger.error(f"Error importing app_standalone via package: {str(e2)}")
        
        # Fall back to directly running the code
        logger.info("Falling back to direct execution")
        
        # Display error and environment info
        st.set_page_config(page_title="Commodity Dashboard - Error", page_icon="⚠️")
        st.title("Commodity Price Dashboard")
        st.error("Could not load the application.")
        
        st.markdown("### Error Information")
        st.code(f"Direct import error: {str(e)}")
        st.code(f"Package import error: {str(e2)}")
        
        st.markdown("### Environment Information")
        st.code(f"Python version: {sys.version}")
        st.code(f"Working directory: {os.getcwd()}")
        
        # List files in current directory
        try:
            files = os.listdir(".")
            st.code(f"Files in current directory: {files}")
        except Exception as e3:
            st.code(f"Could not list files: {str(e3)}")