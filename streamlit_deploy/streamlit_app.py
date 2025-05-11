"""
Streamlit Cloud deployment entry point.
Tries different approaches to ensure the app runs successfully.
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

def main():
    """
    Main entry point with fallback options.
    """
    try:
        logger.info("Starting Streamlit Cloud app...")
        
        # First try to run the simplified app for testing
        logger.info("Trying to run simple test app...")
        try:
            from streamlit_deploy.simple_app import main as simple_main
            return simple_main()
        except Exception as e1:
            logger.warning(f"Error running simple app: {str(e1)}")
            
            # Try to run the full app
            try:
                # Add project root to sys.path
                logger.info("Adding project root to sys.path...")
                PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sys.path.append(PROJECT_ROOT)
                
                logger.info("Trying to run full app...")
                from src.ui.dashboard import Dashboard
                dashboard = Dashboard()
                dashboard.run()
                return
            except Exception as e2:
                logger.warning(f"Error running full app: {str(e2)}")
                
                # Fall back to a basic Streamlit interface
                st.set_page_config(page_title="Commodity Dashboard", page_icon="📊", layout="wide")
                st.title("Commodity Price Dashboard")
                
                st.error("Unable to load the full dashboard at this time.")
                st.markdown("### Troubleshooting Information")
                
                with st.expander("Environment Information"):
                    st.code(f"Python version: {sys.version}")
                    st.code(f"Current directory: {os.getcwd()}")
                    st.code(f"Files in current directory: {os.listdir('.')}")
                    
                    try:
                        st.code(f"Files in parent directory: {os.listdir('..')}")
                    except Exception as e:
                        st.code(f"Unable to list parent directory: {str(e)}")
                
                with st.expander("Error Details"):
                    st.text(f"Simple app error: {str(e1)}")
                    st.text(f"Full app error: {str(e2)}")
                
                # Provide a way to contact support
                st.markdown("""
                Please contact support with the information shown in the troubleshooting section above.
                """)
                
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}", exc_info=True)
        # Fallback to absolute minimum interface
        st.title("Commodity Price Dashboard")
        st.error("Unable to initialize the application. Please try again later.")
        st.code(f"Error: {str(e)}")

if __name__ == "__main__":
    main()