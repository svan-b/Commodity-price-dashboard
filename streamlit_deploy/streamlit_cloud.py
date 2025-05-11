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
    Main entry point with fallback options.
    """
    try:
        logger.info("Starting Streamlit Cloud app...")

        # Try to ensure directories exist
        try:
            from setup_cloud import ensure_directories
            ensure_directories()
        except Exception as setup_error:
            logger.warning(f"Error ensuring directories: {str(setup_error)}")

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

                # Import the optimized StreamlitDataLogger
                from streamlit_deploy.optimized_data_logger import StreamlitDataLogger

                # Import and modify the Dashboard class
                from src.ui.dashboard import Dashboard

                # Patch Dashboard to use cloud-optimized components
                original_init = Dashboard.__init__

                def patched_init(self):
                    """Patched initialization with cloud optimizations"""
                    from src.data.bloomberg_api import BloombergAPI
                    from src.data.data_validator import DataValidator

                    # Initialize with cloud-optimized services
                    self.bloomberg_api = BloombergAPI()
                    self.data_validator = DataValidator()
                    self.data_logger = StreamlitDataLogger(log_dir="logs")
                    self.configure_page()

                # Apply the patch
                Dashboard.__init__ = patched_init

                # Add data caching
                @st.cache_data(ttl=3600)
                def get_cached_commodity_data(commodity, start_date, end_date, freq):
                    """Cache commodity data to reduce API calls"""
                    from src.data.bloomberg_api import BloombergAPI
                    return BloombergAPI().get_commodity_data(commodity, start_date, end_date, freq)

                # Patch Bloomberg API
                from src.data.bloomberg_api import BloombergAPI
                original_get_data = BloombergAPI.get_commodity_data

                def patched_get_data(self, commodity_name, start_date=None, end_date=None, freq='daily'):
                    return get_cached_commodity_data(commodity_name, start_date, end_date, freq)

                BloombergAPI.get_commodity_data = patched_get_data

                logger.info("Trying to run full app...")

                # Add Streamlit Cloud indicator
                def add_cloud_indicator():
                    st.sidebar.markdown("""
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 0.8rem;">
                        <p style="margin: 0;">Running on Streamlit Cloud</p>
                        <p style="margin: 5px 0 0 0;">Optimized for cloud deployment</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Try to monkey patch the dashboard run method to add the indicator
                original_run = Dashboard.run

                def patched_run(self):
                    add_cloud_indicator()
                    return original_run(self)

                Dashboard.run = patched_run

                # Run the dashboard
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