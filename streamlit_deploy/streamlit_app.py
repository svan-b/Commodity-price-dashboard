"""
Streamlit Cloud entry point for the Commodity Price Dashboard.
Optimized version for reliable hosting with reduced disk usage.
"""

import os
import sys
import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np

# Configure logging to stderr to avoid disk writes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Import the optimized data logger
from streamlit_deploy.optimized_data_logger import StreamlitDataLogger

# Import project modules
from src.config import (
    TECK_BLUE, COPPER_ORANGE, BACKGROUND_WHITE, TEXT_COLOR,
    DASHBOARD_TITLE, DASHBOARD_SUBTITLE,
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

# Modify Dashboard class to use the optimized data logger
from src.ui.dashboard import Dashboard

# Before running the main Dashboard, patch it to use our optimized logger
original_init = Dashboard.__init__

def optimized_init(self):
    """Optimized initialization that uses the StreamlitDataLogger"""
    # Initialize Bloomberg API and DataValidator
    self.bloomberg_api = BloombergAPI()
    self.data_validator = DataValidator()
    
    # Use the optimized data logger instead of the standard one
    self.data_logger = StreamlitDataLogger(log_dir="logs")
    
    # Call the configure_page method
    self.configure_page()
    
    logger.info("Dashboard initialized with optimized data logger")

# Apply the patch
Dashboard.__init__ = optimized_init

def main():
    """
    Main entry point for the Streamlit app
    """
    # Set page title and favicon
    st.set_page_config(
        page_title=DASHBOARD_TITLE,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add caching for expensive operations
    @st.cache_data(ttl=3600)  # Cache for one hour
    def get_cached_commodity_data(commodity, start_date, end_date, freq):
        return BloombergAPI().get_commodity_data(commodity, start_date, end_date, freq)
    
    # Add a note about Streamlit Cloud deployment
    st.sidebar.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 0.8rem;">
        <p style="margin: 0;">This dashboard is running on Streamlit Cloud.</p>
        <p style="margin: 5px 0 0 0;">Some features may be optimized for cloud deployment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create and run the dashboard
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()