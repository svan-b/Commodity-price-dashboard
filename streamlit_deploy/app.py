"""
Commodity Price Dashboard - Streamlit Cloud Deployment
Streamlined version for reliable hosting
"""

import os
import sys
import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np

# Configure logging - use streamlit's cache directory for logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Add project root to path so we can import modules
# Get the directory of this file and go up one level
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Import project modules
from src.config import (
    TECK_BLUE, COPPER_ORANGE, BACKGROUND_WHITE, TEXT_COLOR,
    DASHBOARD_TITLE, DASHBOARD_SUBTITLE,
    DEFAULT_TIMEFRAME, DEFAULT_DATA_FREQUENCY,
    AVAILABLE_TIMEFRAMES, AVAILABLE_FREQUENCIES,
    CATEGORIES, COMMODITIES
)
from src.utils.data_logger import DataLogger
from src.data.bloomberg_api import BloombergAPI
from src.data.data_validator import DataValidator
from src.utils.helpers import (
    format_price, calculate_change, create_price_chart,
    create_multi_commodity_chart, get_data_update_text,
    format_change_value
)
from src.ui.dashboard import Dashboard

def main():
    """
    Main entry point for the Streamlit app
    """
    # Create and run the dashboard
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()