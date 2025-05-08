"""
Data validation module for commodity price data.
Performs data quality checks and generates data validation reports.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataValidator:
    """Validates commodity price data for quality and consistency."""
    
    def __init__(self):
        """Initialize the data validator."""
        logger.info("Data validator initialized")
        
    def validate_dataframe(self, df, commodity_name):
        """
        Validate a dataframe for data quality issues.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            commodity_name (str): Name of the commodity
            
        Returns:
            dict: Validation results with issues and metrics
        """
        if df.empty:
            logger.warning(f"Empty dataframe for {commodity_name}")
            return {
                "commodity": commodity_name,
                "valid": False,
                "issues": ["No data available"],
                "metrics": {}
            }
            
        # Check required columns
        required_columns = ['Date', 'Price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Missing columns for {commodity_name}: {missing_columns}")
            return {
                "commodity": commodity_name,
                "valid": False,
                "issues": [f"Missing required columns: {', '.join(missing_columns)}"],
                "metrics": {}
            }
            
        # Initialize results
        issues = []
        metrics = {}
        
        # Check for NaN values
        nan_count = df['Price'].isna().sum()
        if nan_count > 0:
            issues.append(f"Contains {nan_count} missing values")
            
        # Check for negative prices (usually not valid for commodities)
        neg_count = (df['Price'] < 0).sum()
        if neg_count > 0:
            issues.append(f"Contains {neg_count} negative prices")
            
        # Check date order and continuity
        if not df['Date'].is_monotonic_increasing:
            issues.append("Dates are not in ascending order")
            
        # Check for duplicated dates
        duplicate_dates = df['Date'].duplicated().sum()
        if duplicate_dates > 0:
            issues.append(f"Contains {duplicate_dates} duplicate dates")
            
        # Check for future dates (data from the future)
        future_dates = (df['Date'] > datetime.now()).sum()
        if future_dates > 0:
            issues.append(f"Contains {future_dates} dates in the future")
            
        # Calculate basic metrics
        metrics["count"] = len(df)
        metrics["min_price"] = df['Price'].min()
        metrics["max_price"] = df['Price'].max()
        metrics["mean_price"] = df['Price'].mean()
        metrics["median_price"] = df['Price'].median()
        metrics["std_dev"] = df['Price'].std()
        metrics["date_range"] = [df['Date'].min(), df['Date'].max()]
        
        # Check for outliers using Z-score
        z_scores = np.abs((df['Price'] - df['Price'].mean()) / df['Price'].std())
        outliers = (z_scores > 3).sum()
        if outliers > 0:
            issues.append(f"Contains {outliers} potential outliers (|z-score| > 3)")
            metrics["outliers"] = outliers
            
        # Check for sudden price jumps (more than 50% change)
        df_sorted = df.sort_values('Date')
        df_sorted['price_pct_change'] = df_sorted['Price'].pct_change().abs()
        large_jumps = (df_sorted['price_pct_change'] > 0.5).sum()
        if large_jumps > 0:
            issues.append(f"Contains {large_jumps} large price jumps (>50% change)")
            metrics["large_jumps"] = large_jumps
            
        return {
            "commodity": commodity_name,
            "valid": len(issues) == 0,
            "issues": issues,
            "metrics": metrics
        }
    
    def validate_all_data(self, data_dict):
        """
        Validate all commodity data in a dictionary.
        
        Args:
            data_dict (dict): Dictionary of commodity name to DataFrame
            
        Returns:
            dict: Validation results for all commodities
        """
        results = {}
        
        for commodity_name, df in data_dict.items():
            results[commodity_name] = self.validate_dataframe(df, commodity_name)
            
        return results
    
    def get_validation_summary(self, validation_results):
        """
        Create a summary of validation results.
        
        Args:
            validation_results (dict): Results from validate_all_data
            
        Returns:
            dict: Summary of validation with counts and details
        """
        valid_count = sum(1 for result in validation_results.values() if result['valid'])
        
        commodities_with_issues = {
            commodity: details['issues'] 
            for commodity, details in validation_results.items() 
            if not details['valid']
        }
        
        return {
            "total_commodities": len(validation_results),
            "valid_commodities": valid_count,
            "commodities_with_issues": len(commodities_with_issues),
            "issue_details": commodities_with_issues
        }