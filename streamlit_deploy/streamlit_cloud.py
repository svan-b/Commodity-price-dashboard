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
            
        # Configure project paths
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(PROJECT_ROOT)
        
        try:
            # Import necessary components for the dashboard
            logger.info("Importing dashboard components...")
            
            # First import the optimized data logger
            from streamlit_deploy.optimized_data_logger import StreamlitDataLogger
            
            # Patch Bloomberg API to use sample data in cloud environment
            from streamlit_deploy.mock_bloomberg import patch_bloomberg_api
            patch_bloomberg_api()

            # Now import core modules from the project
            from src.data.bloomberg_api import BloombergAPI
            from src.data.data_validator import DataValidator
            from src.ui.dashboard import Dashboard
            
            # Setup data caching to improve performance
            @st.cache_data(ttl=3600)  # Cache for one hour
            def get_cached_commodity_data(commodity, start_date, end_date, freq):
                """Cache commodity data to reduce API calls and improve performance"""
                api = BloombergAPI()
                return api.get_commodity_data(commodity, start_date, end_date, freq)
            
            # Patch the Dashboard class to use our optimized components
            original_init = Dashboard.__init__
            
            def patched_init(self):
                """Optimized initialization for Streamlit Cloud"""
                # Initialize Bloomberg API and DataValidator
                self.bloomberg_api = BloombergAPI()
                self.data_validator = DataValidator()
                
                # Use our optimized data logger
                self.data_logger = StreamlitDataLogger(log_dir="logs")
                
                # Configure the page
                self.configure_page()
                
                logger.info("Dashboard initialized with cloud optimizations")
            
            # Apply the patch
            Dashboard.__init__ = patched_init
            
            # Patch Bloomberg API to use caching
            original_get_commodity_data = BloombergAPI.get_commodity_data
            
            def patched_get_commodity_data(self, commodity_name, start_date=None, end_date=None, freq='daily'):
                """Use cached data retrieval for better performance"""
                return get_cached_commodity_data(commodity_name, start_date, end_date, freq)
            
            # Apply the patch to use caching
            BloombergAPI.get_commodity_data = patched_get_commodity_data
            
            # Add deployment indicator to the sidebar
            def add_deployment_indicator():
                st.sidebar.markdown("""
                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 0.8rem;">
                    <p style="margin: 0;">Running on <b>Streamlit Cloud</b></p>
                    <p style="margin: 5px 0 0 0;">Optimized for cloud deployment</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Add the indicator after the Dashboard is initialized
            original_run = Dashboard.run
            
            def patched_run(self):
                """Add deployment indicator to the dashboard"""
                add_deployment_indicator()
                return original_run(self)
            
            Dashboard.run = patched_run
            
            # Run the full dashboard
            logger.info("Starting dashboard with cloud optimizations...")
            dashboard = Dashboard()
            dashboard.run()
            
        except Exception as e:
            logger.error(f"Error running full dashboard: {str(e)}", exc_info=True)
            
            # Fall back to the simplified app if the full dashboard fails
            logger.info("Falling back to simplified app...")
            try:
                from streamlit_deploy.simple_app import main as simple_main
                
                # Add an error message to the simple app
                original_simple_main = simple_main
                
                def patched_simple_main():
                    st.error("The full dashboard could not be loaded. Using simplified app instead.")
                    st.expander("Error Details").code(str(e))
                    return original_simple_main()
                
                simple_main = patched_simple_main
                return simple_main()
                
            except Exception as e2:
                logger.error(f"Error running simplified app: {str(e2)}", exc_info=True)
                
                # Last resort: show a basic error page
                st.set_page_config(page_title="Commodity Dashboard", page_icon="📊", layout="wide")
                st.title("Commodity Price Dashboard")
                
                st.error("Unable to load the dashboard at this time.")
                st.markdown("### Troubleshooting Information")
                
                with st.expander("Environment Information"):
                    st.code(f"Python version: {sys.version}")
                    st.code(f"Current directory: {os.getcwd()}")
                    st.code(f"Files in current directory: {os.listdir('.')}")
                    
                    try:
                        st.code(f"Parent directory: {os.path.dirname(os.getcwd())}")
                        st.code(f"Files in parent directory: {os.listdir('..')}")
                    except Exception as e3:
                        st.code(f"Unable to list parent directory: {str(e3)}")
                    
                    try:
                        st.code(f"Files in src directory: {os.listdir('src')}")
                    except Exception as e4:
                        st.code(f"Unable to list src directory: {str(e4)}")
                
                with st.expander("Error Details"):
                    st.markdown("**Full Dashboard Error:**")
                    st.code(str(e))
                    st.markdown("**Simple App Error:**")
                    st.code(str(e2))
    
    except Exception as e:
        # Absolute last resort
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        st.title("Commodity Price Dashboard")
        st.error("Critical error. Please try again later.")
        st.code(f"Error: {str(e)}")

if __name__ == "__main__":
    main()