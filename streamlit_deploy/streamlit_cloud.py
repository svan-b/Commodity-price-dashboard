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

# Ensure all required directories exist
from setup_cloud import ensure_directories
ensure_directories()

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Import the optimized StreamlitDataLogger
from streamlit_deploy.optimized_data_logger import StreamlitDataLogger

# Get configurations and necessary modules
from src.config import (
    TECK_BLUE, DASHBOARD_TITLE, DASHBOARD_SUBTITLE,
    DEFAULT_TIMEFRAME, DEFAULT_DATA_FREQUENCY,
    AVAILABLE_TIMEFRAMES, AVAILABLE_FREQUENCIES,
    CATEGORIES, COMMODITIES
)
from src.data.bloomberg_api import BloombergAPI
from src.data.data_validator import DataValidator
from src.utils.helpers import (
    format_price, calculate_change, create_price_chart,
    create_multi_commodity_chart, get_data_update_text,
    format_change_value
)

# Import and modify the Dashboard class
from src.ui.dashboard import Dashboard

# Create a modified init method for the Dashboard class
original_init = Dashboard.__init__

def patched_init(self):
    """Patched initialization that uses optimized components for Streamlit Cloud"""
    # Initialize services
    self.bloomberg_api = BloombergAPI()
    self.data_validator = DataValidator()
    
    # Use the cloud-optimized data logger instead
    self.data_logger = StreamlitDataLogger(log_dir="logs")
    
    # Configure the page
    self.configure_page()
    
    logger.info("Dashboard initialized with cloud optimizations")

# Apply the patch
Dashboard.__init__ = patched_init

# Add performance optimizations
@st.cache_data(ttl=3600)  # Cache for one hour
def get_cached_commodity_data(commodity, start_date, end_date, freq):
    """Cache commodity data to reduce API calls and improve performance"""
    return BloombergAPI().get_commodity_data(commodity, start_date, end_date, freq)

# Modify the Bloomberg API to use caching
original_get_commodity_data = BloombergAPI.get_commodity_data

def patched_get_commodity_data(self, commodity_name, start_date=None, end_date=None, freq='daily'):
    """Patched method that uses caching for better performance"""
    return get_cached_commodity_data(commodity_name, start_date, end_date, freq)

# Apply the patch to use caching
BloombergAPI.get_commodity_data = patched_get_commodity_data

def main():
    """Main entry point for the Streamlit Cloud app"""
    # Configure page settings
    st.set_page_config(
        page_title=DASHBOARD_TITLE,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add a small note about Streamlit Cloud deployment
    st.sidebar.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 0.8rem;">
        <p style="margin: 0;">Running on Streamlit Cloud</p>
        <p style="margin: 5px 0 0 0;">Optimized for cloud deployment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize and run the dashboard
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()