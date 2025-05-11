"""
Mock Bloomberg API module for Streamlit Cloud deployment.
Ensures the app works without a Bloomberg terminal by always using sample data.
"""

import logging
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

def patch_bloomberg_api():
    """Patch the Bloomberg API to always use sample data in cloud environment."""
    logger.info("Patching Bloomberg API to use sample data for cloud deployment")
    
    try:
        # Import the original Bloomberg API module
        from src.data.bloomberg_api import BloombergAPI
        
        # Store the original methods
        original_get_historical_data = BloombergAPI.get_historical_data
        
        # Create patch method that always returns sample data
        def patched_get_historical_data(self, ticker, start_date=None, end_date=None, freq='daily'):
            """Always use sample data in cloud environment."""
            logger.info(f"Using sample data for {ticker} (cloud mode)")
            
            # Find the commodity for this ticker
            from src.config import COMMODITIES
            
            commodity_name = None
            for commodity in COMMODITIES:
                if commodity['preferred_ticker'] == ticker or commodity['alternative_ticker'] == ticker:
                    commodity_name = commodity['name']
                    break
            
            # If we can't find a match, return empty DataFrame
            if not commodity_name:
                logger.warning(f"No commodity found for ticker {ticker}")
                return pd.DataFrame(columns=['Date', 'Price'])
            
            # Return sample data for this commodity
            return self._get_sample_data_for_commodity(commodity_name, start_date, end_date, freq)
        
        # Add a method to generate sample data for a specific commodity
        def get_sample_data_for_commodity(self, commodity_name, start_date=None, end_date=None, freq='daily'):
            """Generate sample data for a specific commodity."""
            # Import generate_sample_data from config
            from src.config import generate_sample_data, COMMODITIES
            
            # Get the sample data
            sample_data = generate_sample_data()
            
            # If the commodity exists in sample data, return it with date filtering
            if commodity_name in sample_data:
                df = sample_data[commodity_name].copy()
                
                # Filter by date if provided
                if start_date:
                    start_dt = pd.to_datetime(start_date)
                    df = df[df['Date'] >= start_dt]
                if end_date:
                    end_dt = pd.to_datetime(end_date)
                    df = df[df['Date'] <= end_dt]
                
                # Return the filtered data
                return df
            else:
                logger.warning(f"No sample data available for {commodity_name}")
                return pd.DataFrame(columns=['Date', 'Price'])
        
        # Add the new method to the class
        BloombergAPI._get_sample_data_for_commodity = get_sample_data_for_commodity
        
        # Apply the patch
        BloombergAPI.get_historical_data = patched_get_historical_data
        
        # Also patch get_commodity_data to log that we're using sample data
        original_get_commodity_data = BloombergAPI.get_commodity_data
        
        def patched_get_commodity_data(self, commodity_name, start_date=None, end_date=None, freq='daily'):
            """Get cloud-friendly sample data for a commodity."""
            logger.info(f"Getting sample data for {commodity_name} (cloud mode)")
            
            # Use the original method (which will now use our patched get_historical_data)
            df = original_get_commodity_data(self, commodity_name, start_date, end_date, freq)
            
            # Add a cloud indicator to the dataframe
            if not df.empty:
                df['Data Source'] = 'Cloud Sample Data'
            
            return df
        
        # Apply the patch
        BloombergAPI.get_commodity_data = patched_get_commodity_data
        
        logger.info("Successfully patched Bloomberg API for cloud deployment")
        return True
        
    except Exception as e:
        logger.error(f"Error patching Bloomberg API: {str(e)}", exc_info=True)
        return False