"""
Standalone Bloomberg API mock for Streamlit Cloud.
This completely replaces the real Bloomberg API without any dependencies on xbbg.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class MockBloombergAPI:
    """
    Standalone mock implementation of BloombergAPI that doesn't depend on xbbg.
    This is used for Streamlit Cloud where Bloomberg Terminal access is not available.
    """
    
    def __init__(self):
        """Initialize the mock Bloomberg API client."""
        self.sample_data = self._generate_sample_data()
        logger.info("Mock Bloomberg API initialized for cloud deployment")
    
    def get_commodity_tickers(self, category=None):
        """
        Get list of all tickers or filtered by category.
        
        Args:
            category (str, optional): Filter commodities by category.
        
        Returns:
            dict: Dictionary of commodity names to their preferred ticker
        """
        # Import commodities directly to avoid circular imports
        import json
        
        # Load commodities from a simplified dict to avoid importing from config
        commodities = self._get_commodities()
        
        tickers = {}
        for commodity in commodities:
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
        # Find the commodity for this ticker
        commodities = self._get_commodities()
        commodity_name = None
        
        for commodity in commodities:
            if commodity['preferred_ticker'] == ticker or commodity['alternative_ticker'] == ticker:
                commodity_name = commodity['name']
                break
        
        if not commodity_name:
            logger.warning(f"No commodity found for ticker {ticker}")
            return pd.DataFrame(columns=['Date', 'Price'])
        
        # Get sample data for this commodity
        if commodity_name in self.sample_data:
            df = self.sample_data[commodity_name].copy()
            
            # Filter by date if provided
            if start_date:
                start_dt = pd.to_datetime(start_date)
                df = df[df['Date'] >= start_dt]
                
            if end_date:
                end_dt = pd.to_datetime(end_date)
                df = df[df['Date'] <= end_dt]
                
            # Resample based on frequency if not daily
            if freq == 'weekly':
                df = df.set_index('Date')
                # Use last day of week for financial data
                df = df.resample('W-FRI').mean()
                df['Price'] = df['Price'].ffill().bfill()
                df = df.reset_index()
                
            elif freq == 'monthly':
                df = df.set_index('Date')
                # Use last business day of month
                df = df.resample('BM').mean()
                df['Price'] = df['Price'].ffill().bfill()
                df = df.reset_index()
                
                # Drop the last row if it's the current month (incomplete data)
                if not df.empty and df['Date'].iloc[-1].month == datetime.now().month:
                    df = df[:-1]
            
            return df
        else:
            logger.warning(f"No sample data available for {commodity_name}")
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
        logger.info(f"Getting sample data for {commodity_name} (cloud mode)")
        
        # Find the commodity in our list
        commodities = self._get_commodities()
        commodity = next((c for c in commodities if c['name'] == commodity_name), None)
        
        if not commodity:
            logger.warning(f"Commodity '{commodity_name}' not found in configuration")
            return pd.DataFrame(columns=['Date', 'Price'])
        
        # Get sample data
        if commodity_name in self.sample_data:
            df = self.sample_data[commodity_name].copy()
            
            # Filter by date if provided
            if start_date:
                start_dt = pd.to_datetime(start_date)
                df = df[df['Date'] >= start_dt]
                
            if end_date:
                end_dt = pd.to_datetime(end_date)
                df = df[df['Date'] <= end_dt]
            
            # Add metadata columns
            df['Commodity'] = commodity_name
            df['Units'] = commodity['units']
            df['Type'] = commodity['type']
            df['Data Source'] = "Streamlit Cloud Sample Data"
            df['Ticker'] = commodity['preferred_ticker'] or commodity['alternative_ticker'] or 'N/A'
            
            # Sort by date
            df = df.sort_values('Date')
            
            return df
        else:
            logger.warning(f"No sample data available for {commodity_name}")
            return pd.DataFrame(columns=['Date', 'Price'])
    
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
        commodities = self._get_commodities()
        commodities_to_fetch = [c for c in commodities if not category or c['category'] == category]
        
        for commodity in commodities_to_fetch:
            commodity_name = commodity['name']
            df = self.get_commodity_data(commodity_name, start_date, end_date, freq)
            
            if not df.empty:
                results[commodity_name] = df
        
        return results
    
    def _get_commodities(self):
        """Get a simplified version of the commodities configuration."""
        # Import from config if available, otherwise use a basic set of commodities
        try:
            # Try to import from config
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.config import COMMODITIES
            return COMMODITIES
        except ImportError:
            # Basic fallback commodities
            return [
                {
                    "name": "Copper (Cu)",
                    "category": "base_metals",
                    "preferred_ticker": "LMCADY Comdty",
                    "alternative_ticker": None,
                    "type": "Spot (LME Cash)",
                    "units": "USD/MT",
                    "data_source": "Sample Data"
                },
                {
                    "name": "Gold (Au)",
                    "category": "precious_metals",
                    "preferred_ticker": "XAU BGN Curncy",
                    "alternative_ticker": "XAU",
                    "type": "Spot",
                    "units": "USD/troy oz",
                    "data_source": "Sample Data"
                },
                {
                    "name": "Oil (WTI)",
                    "category": "energy",
                    "preferred_ticker": "USCRWTIC Index",
                    "alternative_ticker": None,
                    "type": "Spot",
                    "units": "USD/barrel",
                    "data_source": "Sample Data"
                }
            ]
    
    def _generate_sample_data(self):
        """Generate sample price data for commodities."""
        commodities = self._get_commodities()
        today = datetime.now()
        
        # Generate data spanning from 5 years ago to today
        start_date = today - timedelta(days=5*365)
        
        # Generate daily data points
        dates = pd.date_range(start=start_date, end=today, freq='D')
        
        # Generate sample data for all commodities
        sample_data = {}
        
        for commodity in commodities:
            commodity_name = commodity['name']
            
            # Set appropriate price range based on commodity type
            if 'units' in commodity:
                if 'USD/MT' in commodity['units']:
                    base = 2000
                    volatility = 300
                elif 'USD/lb' in commodity['units']:
                    base = 3
                    volatility = 0.5
                elif 'USD/troy oz' in commodity['units']:
                    if 'Gold' in commodity_name:
                        base = 1800
                        volatility = 200
                    elif 'Silver' in commodity_name:
                        base = 25
                        volatility = 3
                    elif 'Platinum' in commodity_name:
                        base = 1000
                        volatility = 100
                    else:
                        base = 100
                        volatility = 20
                elif 'USD/kg' in commodity['units']:
                    base = 20
                    volatility = 5
                elif 'USD/barrel' in commodity['units']:
                    base = 80
                    volatility = 15
                elif 'CNY' in commodity['units']:
                    base = 15000
                    volatility = 2000
                else:
                    base = 100
                    volatility = 20
            else:
                base = 100
                volatility = 20
            
            # Create a time series with trend and seasonality
            t = np.linspace(0, 1, len(dates))
            
            # Trend with some randomness
            trend = base + volatility * 0.5 * np.sin(t * 4)
            seasonality = volatility * 0.1 * np.sin(np.linspace(0, 6, len(dates)))
            noise = np.random.normal(0, volatility * 0.05, size=len(dates))
            
            # Combine components
            prices = trend + seasonality + noise
            
            # Use a rolling mean to smooth out the data
            prices = pd.Series(prices).rolling(window=3, min_periods=1).mean().values
            
            # Ensure no negative prices
            prices = np.maximum(prices, base * 0.7)
            
            # Create dataframe
            sample_data[commodity_name] = pd.DataFrame({
                'Date': dates,
                'Price': prices
            })
        
        return sample_data