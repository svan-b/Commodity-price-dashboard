"""
Optimized DataLogger implementation for Streamlit Cloud deployment
that limits disk usage and prevents app crashes.
"""

import logging
import os
import json
import csv
import pandas as pd
from datetime import datetime
import numpy as np
import streamlit as st

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle pandas Timestamp objects and other non-serializable types."""
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if pd.isna(obj):
            return None
        return super().default(obj)

def make_json_serializable(obj):
    """
    Convert objects to JSON-serializable formats.

    Args:
        obj: Any Python object

    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [make_json_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    else:
        return obj

class StreamlitDataLogger:
    """
    Memory-optimized data logger for Streamlit Cloud.
    Reduces disk writes and uses session state for caching.
    """
    
    def __init__(self, log_dir="logs"):
        """
        Initialize the data logger with minimized disk usage.
        
        Args:
            log_dir (str): Directory to store log files
        """
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Use streamlit's cache directory for logs
        self.log_dir = log_dir
        
        # Create log directory only if needed
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize session state for caching validation results
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = {}
        
        self.logger.info(f"StreamlitDataLogger initialized with log directory: {self.log_dir}")
    
    def log_validation_results(self, validation_results, timestamp=None):
        """
        Log validation results using Streamlit session state.

        Args:
            validation_results (dict): Validation results
            timestamp (datetime, optional): Timestamp for the log
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Store in session state instead of writing to disk
        st.session_state.validation_results = {
            "timestamp": timestamp.isoformat(),
            "results": make_json_serializable(validation_results)
        }
        
        self.logger.info("Validation results cached in session state")
    
    def capture_data_snapshot(self, data_dict, filters=None, timestamp=None):
        """
        Cache data snapshot in session state (minimal version).
        
        Args:
            data_dict (dict): Dictionary of commodity data
            filters (dict, optional): Filter settings
            timestamp (datetime, optional): Timestamp for snapshot
        """
        # Only store metadata in session state, not full dataframes
        commodity_counts = {name: len(df) for name, df in data_dict.items() if not df.empty}
        
        if 'snapshots' not in st.session_state:
            st.session_state.snapshots = []
            
        st.session_state.snapshots.append({
            "timestamp": datetime.now().isoformat(),
            "commodity_counts": commodity_counts,
            "filters": make_json_serializable(filters) if filters else None
        })
        
        # Limit the number of snapshots to prevent memory issues
        if len(st.session_state.snapshots) > 10:
            st.session_state.snapshots = st.session_state.snapshots[-10:]
            
        self.logger.info(f"Data snapshot metadata cached in session state")
    
    def log_price_comparison(self, commodity_name, current_price, previous_prices, timestamp=None):
        """
        Cache price comparison in session state (minimal disk usage).

        Args:
            commodity_name (str): Name of the commodity
            current_price (float): Current price
            previous_prices (dict): Dictionary of previous prices
            timestamp (datetime, optional): Timestamp for the log
        """
        # Convert any numpy types to native Python types
        if isinstance(current_price, (np.integer, np.floating)):
            current_price = float(current_price)
        
        # Initialize price comparison in session state
        if 'price_comparisons' not in st.session_state:
            st.session_state.price_comparisons = {}
            
        # Store the most recent comparison only
        st.session_state.price_comparisons[commodity_name] = {
            "timestamp": datetime.now().isoformat(),
            "current_price": current_price,
            "previous_prices": make_json_serializable(previous_prices)
        }
    
    def generate_data_quality_report(self):
        """
        Generate a simple HTML data quality report that can be downloaded from the browser.
        Uses cached data instead of disk reads.

        Returns:
            str: HTML content of the report
        """
        # Get summary metrics from session state
        summary_data = []
        
        # Count commodities with validation results
        validation_results = st.session_state.get('validation_results', {}).get('results', {})
        if validation_results:
            valid_count = sum(1 for result in validation_results.values() if result.get('valid', False))
            invalid_count = len(validation_results) - valid_count
            
            summary_data.append(("Total Commodities", len(validation_results)))
            summary_data.append(("Valid Commodities", valid_count))
            summary_data.append(("Commodities with Issues", invalid_count))
            
            # Count issue types
            issue_counts = {}
            for result in validation_results.values():
                if not result.get('valid', True):
                    for issue in result.get('issues', []):
                        issue_counts[issue] = issue_counts.get(issue, 0) + 1
                        
            if issue_counts:
                issue_summary = ", ".join([f"{issue} ({count})" for issue, count in issue_counts.items()])
                summary_data.append(("Common Issues", issue_summary))
            else:
                summary_data.append(("Common Issues", "None found"))
        else:
            summary_data.append(("Validation Data", "No validation data available"))
            
        # Count snapshots from session state
        snapshot_count = len(st.session_state.get('snapshots', []))
        summary_data.append(("Data Snapshots Captured", snapshot_count))

        # Generate HTML report
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Commodity Data Quality Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: #00103f;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 25px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .section {{
            margin-bottom: 30px;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>Commodity Data Quality Report</h1>
    <div class="summary">
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="section">
        <h2>Data Quality Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            {"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in summary_data)}
        </table>
    </div>

    <div class="section">
        <h2>Streamlit Cloud Deployment</h2>
        <p>This dashboard is deployed on Streamlit Cloud with optimized settings for:</p>
        <ul>
            <li>Minimal disk usage</li>
            <li>Memory efficiency</li>
            <li>Streamlined logging</li>
            <li>Session-based data caching</li>
        </ul>
        <p>This helps ensure the application remains responsive and avoids service interruptions.</p>
    </div>
</body>
</html>
"""
        self.logger.info("Data quality report generated for browser download")
        return html_content