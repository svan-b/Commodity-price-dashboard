"""
Main entry point for Streamlit Cloud deployment.
Simple wrapper to run the streamlit_cloud.py module.
"""

import os
import sys
import logging

# Configure logging to stdout to avoid file operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    # Import and run the cloud module's main function
    from streamlit_deploy.streamlit_cloud import main
    logger.info("Starting Streamlit Cloud app...")
    main()
except Exception as e:
    logger.error(f"Error starting app: {str(e)}", exc_info=True)
    import traceback
    traceback.print_exc()
    
    # Print environment information for debugging
    logger.info("Python version: %s", sys.version)
    logger.info("Current directory: %s", os.getcwd())
    logger.info("Files in current directory: %s", os.listdir('.'))
    logger.info("Files in parent directory: %s", os.listdir('..'))
    
    # As a fallback, try to import directly from the current directory
    try:
        logger.info("Attempting direct import...")
        from streamlit_cloud import main
        main()
    except Exception as e2:
        logger.error(f"Fallback failed: {str(e2)}", exc_info=True)