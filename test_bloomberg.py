#!/usr/bin/env python3
"""
Test script to check if Bloomberg API is accessible and working.
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Test Bloomberg API connectivity.
    """
    try:
        logger.info("Testing Bloomberg API import...")
        
        try:
            import xbbg
            logger.info("Successfully imported xbbg")
        except ImportError as e:
            logger.error(f"Failed to import xbbg: {str(e)}")
            logger.info("Please install it with: pip install xbbg")
            return 1
        
        logger.info("Testing Bloomberg API connectivity...")
        try:
            from xbbg import blp
            
            # Test a simple query
            tickers = ['LMCADY Comdty']  # Copper ticker as example
            start_date = '2023-01-01'
            end_date = '2023-01-31'
            
            logger.info(f"Fetching data for {tickers} from {start_date} to {end_date}...")
            data = blp.bdh(tickers, 'PX_LAST', start_date=start_date, end_date=end_date)
            
            if data is None or data.empty:
                logger.warning("No data received from Bloomberg API")
                logger.info("This could be due to:")
                logger.info("1. Bloomberg Terminal not running")
                logger.info("2. No Bloomberg subscription")
                logger.info("3. The ticker or date range is invalid")
                logger.info("\nThe dashboard will still work with sample data, but real Bloomberg data will not be available.")
            else:
                logger.info(f"Successfully retrieved {len(data)} data points")
                logger.info("Bloomberg API is working correctly!")
                logger.info("\nSample data:")
                logger.info(f"\n{data.head()}")
                
            return 0
                
        except Exception as e:
            logger.error(f"Error testing Bloomberg connectivity: {str(e)}")
            logger.info("The dashboard will still work with sample data, but real Bloomberg data will not be available.")
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())