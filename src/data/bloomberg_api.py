"""
Bloomberg API module for fetching commodity price data.
Uses xbbg to interact with Bloomberg terminal.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from xbbg import blp
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COMMODITIES, generate_sample_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BloombergAPI:
    """Interface for retrieving data from Bloomberg."""
    
    def __init__(self):
        """Initialize the Bloomberg API client."""
        self.sample_data = generate_sample_data()
        logger.info("Bloomberg API client initialized")
    
    def get_commodity_tickers(self, category=None):
        """
        Get list of all tickers or filtered by category.
        
        Args:
            category (str, optional): Filter commodities by category.
                                     Options: 'core', 'strategic', 'industry', 'additional'
        
        Returns:
            dict: Dictionary of commodity names to their preferred ticker
        """
        tickers = {}
        
        for commodity in COMMODITIES:
            if category and commodity['category'] != category:
                continue
                
            if commodity['preferred_ticker']:
                tickers[commodity['name']] = commodity['preferred_ticker']
            elif commodity['alternative_ticker']:
                tickers[commodity['name']] = commodity['alternative_ticker']
                
        return tickers
    
    def get_historical_data(self, ticker, start_date=None, end_date=None, freq='daily'):
        """
        Get historical price data for a ticker.
        
        Args:
            ticker (str): Bloomberg ticker
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            freq (str, optional): Data frequency - 'daily', 'weekly', or 'monthly'
            
        Returns:
            pd.DataFrame: DataFrame with historical price data
        """
        # Check if we're dealing with a commodity that doesn't have Bloomberg data
        for commodity in COMMODITIES:
            if (commodity['preferred_ticker'] == ticker or 
                commodity['alternative_ticker'] == ticker) and ticker is None:
                commodity_name = commodity['name']
                if commodity_name in self.sample_data:
                    logger.info(f"Using sample data for {commodity_name}")
                    sample_df = self.sample_data[commodity_name]
                    
                    # Filter by date if provided
                    if start_date:
                        start_dt = pd.to_datetime(start_date)
                        sample_df = sample_df[sample_df['Date'] >= start_dt]
                    if end_date:
                        end_dt = pd.to_datetime(end_date)
                        sample_df = sample_df[sample_df['Date'] <= end_dt]
                        
                    return sample_df
                else:
                    logger.warning(f"No data available for {commodity_name}")
                    return pd.DataFrame(columns=['Date', 'Price'])
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            # Default to 1 year lookback, or longer for monthly data to ensure enough points
            if freq == 'monthly':
                start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')  # ~10 years
            elif freq == 'weekly':
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')  # ~2 years
            else:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year
            
        logger.info(f"Fetching {freq} data for {ticker} from {start_date} to {end_date}")
        
        try:
            # Fetch daily data from Bloomberg with error handling
            try:
                data = blp.bdh(ticker, 'PX_LAST', start_date=start_date, end_date=end_date)
                
                # Check if data is empty or None
                if data is None or data.empty:
                    logger.warning(f"Empty data returned for {ticker}")
                    return pd.DataFrame(columns=['Date', 'Price'])
                    
            except Exception as e:
                logger.error(f"Error in initial Bloomberg data fetch for {ticker}: {str(e)}")
                # Try with a shorter time range if the initial fetch fails
                try:
                    shorter_start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                    logger.info(f"Retrying with shorter range: {shorter_start_date} to {end_date}")
                    data = blp.bdh(ticker, 'PX_LAST', start_date=shorter_start_date, end_date=end_date)
                    
                    if data is None or data.empty:
                        logger.warning(f"Empty data returned for {ticker} even with shorter range")
                        return pd.DataFrame(columns=['Date', 'Price'])
                        
                except Exception as e2:
                    logger.error(f"Error in fallback Bloomberg data fetch for {ticker}: {str(e2)}")
                    return pd.DataFrame(columns=['Date', 'Price'])
            
            # Format dataframe columns with error handling
            try:
                # Check if data columns are a MultiIndex
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [col[0] for col in data.columns]
                elif len(data.columns) == 0:
                    logger.warning(f"No columns in data for {ticker}")
                    return pd.DataFrame(columns=['Date', 'Price'])
                
                # Reset index to make Date a column
                df = data.reset_index()
                
                # Handle case where the ticker isn't in the columns (can happen with some Bloomberg responses)
                if ticker in df.columns:
                    df = df.rename(columns={ticker: 'Price'})
                elif len(df.columns) > 1:  # If there's a column besides the index/date
                    price_col = [col for col in df.columns if col != 'index'][0]
                    df = df.rename(columns={price_col: 'Price'})
                else:
                    logger.warning(f"Unexpected column structure for {ticker}: {df.columns}")
                    return pd.DataFrame(columns=['Date', 'Price'])
                
                # Rename the index column to Date if it exists
                if 'index' in df.columns:
                    df = df.rename(columns={'index': 'Date'})
                
                # Ensure datetime type for the Date column
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Handle missing values
                if df['Price'].isna().any():
                    missing_count = df['Price'].isna().sum()
                    total_count = len(df)
                    missing_pct = (missing_count / total_count) * 100
                    
                    logger.info(f"{ticker} has {missing_count} missing values out of {total_count} ({missing_pct:.1f}%)")
                    
                    if missing_pct > 50:
                        logger.warning(f"Too many missing values for {ticker}, data may be unreliable")
                    
                    # For pricing data, forward fill is often appropriate
                    # Then backfill any remaining NAs at the beginning
                    df['Price'] = df['Price'].ffill().bfill()
                
                # Filter out any future dates
                today = pd.Timestamp.today()
                df = df[df['Date'] <= today]
                
                # Resample based on frequency if not daily
                if freq == 'weekly':
                    df = df.set_index('Date')
                    # Use last day of week for financial data often makes more sense
                    df = df.resample('W-FRI').mean()
                    # Handle potential missing values after resampling
                    df['Price'] = df['Price'].ffill().bfill()
                    df = df.reset_index()
                    
                elif freq == 'monthly':
                    df = df.set_index('Date')
                    # Use last business day of month for financial data
                    df = df.resample('BM').mean()
                    # Handle potential missing values after resampling
                    df['Price'] = df['Price'].ffill().bfill()
                    df = df.reset_index()
                    
                    # Drop the last row if it's the current month (incomplete data)
                    if not df.empty and df['Date'].iloc[-1].month == datetime.now().month:
                        df = df[:-1]
                
                # Final check for empty dataframe after processing
                if df.empty:
                    logger.warning(f"DataFrame is empty after processing for {ticker}")
                    return pd.DataFrame(columns=['Date', 'Price'])
                
                # Final check for any remaining NaNs
                if df['Price'].isna().any():
                    logger.warning(f"DataFrame still contains NaNs after processing for {ticker}")
                    # As a last resort, drop rows with NaN values
                    df = df.dropna(subset=['Price'])
                
                # Sort by date to ensure chronological order
                df = df.sort_values('Date')
                
                return df
                
            except Exception as e:
                logger.error(f"Error processing data for {ticker}: {str(e)}")
                return pd.DataFrame(columns=['Date', 'Price'])
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            
            # Try alternative ticker if available
            for commodity in COMMODITIES:
                if commodity['preferred_ticker'] == ticker and commodity['alternative_ticker']:
                    alt_ticker = commodity['alternative_ticker']
                    logger.info(f"Trying alternative ticker {alt_ticker} for {commodity['name']}")
                    return self.get_historical_data(alt_ticker, start_date, end_date, freq)
            
            # Return empty dataframe if all options fail
            return pd.DataFrame(columns=['Date', 'Price'])
    
    def get_commodity_data(self, commodity_name, start_date=None, end_date=None, freq='daily'):
        """
        Get historical data for a commodity by name.
        
        Args:
            commodity_name (str): Name of the commodity
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            freq (str, optional): Data frequency - 'daily', 'weekly', or 'monthly'
            
        Returns:
            pd.DataFrame: DataFrame with historical price data
        """
        # Find the commodity configuration
        commodity = next((c for c in COMMODITIES if c['name'] == commodity_name), None)
        
        if not commodity:
            logger.error(f"Commodity '{commodity_name}' not found in configuration")
            return pd.DataFrame(columns=['Date', 'Price'])
            
        # Try preferred ticker first
        df = pd.DataFrame()
        if commodity['preferred_ticker']:
            df = self.get_historical_data(
                commodity['preferred_ticker'], 
                start_date, 
                end_date, 
                freq
            )
            
            # If we got data, add metadata
            if not df.empty:
                # Add metadata columns
                df['Commodity'] = commodity_name
                df['Units'] = commodity['units']
                df['Type'] = commodity['type']
                df['Data Source'] = commodity['data_source']
                df['Ticker'] = commodity['preferred_ticker']
                
        # Try alternative ticker if preferred failed or returned little data
        if df.empty or len(df) < 10:  # Arbitrary threshold for "enough data"
            if commodity['alternative_ticker']:
                alt_df = self.get_historical_data(
                    commodity['alternative_ticker'], 
                    start_date, 
                    end_date, 
                    freq
                )
                
                # If we got alternative data, use it
                if not alt_df.empty:
                    # Add metadata columns
                    alt_df['Commodity'] = commodity_name
                    alt_df['Units'] = commodity['units']
                    alt_df['Type'] = commodity['type']
                    alt_df['Data Source'] = commodity['data_source']
                    alt_df['Ticker'] = commodity['alternative_ticker']
                    
                    # Only replace if the alternative data has more points or if original is empty
                    if df.empty or len(alt_df) > len(df):
                        df = alt_df
                        logger.info(f"Using alternative ticker data for {commodity_name} ({len(df)} data points)")
                    
        # If no tickers or all data retrieval failed, check for sample data
        if df.empty and commodity_name in self.sample_data:
            logger.info(f"Using sample data for {commodity_name} after Bloomberg retrieval failed")
            df = self.sample_data[commodity_name].copy()
            
            # Add metadata columns
            df['Commodity'] = commodity_name
            df['Units'] = commodity['units']
            df['Type'] = commodity['type']
            df['Data Source'] = 'Sample Data'
            df['Ticker'] = 'N/A'
            
        # Final check for empty dataframe
        if df.empty:
            logger.error(f"Failed to retrieve any data for {commodity_name}")
            return pd.DataFrame(columns=['Date', 'Price', 'Commodity', 'Units', 'Type', 'Data Source', 'Ticker'])
            
        return df
    
    def get_all_commodity_data(self, category=None, start_date=None, end_date=None, freq='monthly'):
        """
        Get data for all commodities or filtered by category.
        
        Args:
            category (str, optional): Filter by category
            start_date (str, optional): Start date
            end_date (str, optional): End date
            freq (str, optional): Data frequency
            
        Returns:
            dict: Dictionary of commodity names to their data DataFrames
        """
        results = {}
        
        # Get list of commodities to fetch
        commodities_to_fetch = [c for c in COMMODITIES if not category or c['category'] == category]
        
        for commodity in commodities_to_fetch:
            commodity_name = commodity['name']
            logger.info(f"Fetching data for {commodity_name}")
            
            try:
                df = self.get_commodity_data(commodity_name, start_date, end_date, freq)
                
                if not df.empty:
                    results[commodity_name] = df
                else:
                    logger.warning(f"Empty result for {commodity_name}, skipping")
            except Exception as e:
                logger.error(f"Error fetching {commodity_name}: {str(e)}")
                # Continue with other commodities even if one fails
                continue
                
        logger.info(f"Retrieved data for {len(results)}/{len(commodities_to_fetch)} commodities")
        return results