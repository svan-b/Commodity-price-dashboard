"""
Data logging module for commodity price data.
Provides comprehensive logging of data integrity, validation, and comparison.
"""

import logging
import os
import json
import csv
import pandas as pd
from datetime import datetime
import numpy as np

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

class DataLogger:
    """
    Logs commodity price data for integrity and validation purposes.
    Allows for historical comparison and data quality tracking.
    """
    
    def __init__(self, log_dir="logs"):
        """
        Initialize the data logger.
        
        Args:
            log_dir (str): Directory to store log files
        """
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Create log directory if it doesn't exist
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create subdirectories for different log types
        self.validation_dir = os.path.join(self.log_dir, "validation")
        self.data_capture_dir = os.path.join(self.log_dir, "data_capture")
        self.comparison_dir = os.path.join(self.log_dir, "comparison")
        
        os.makedirs(self.validation_dir, exist_ok=True)
        os.makedirs(self.data_capture_dir, exist_ok=True)
        os.makedirs(self.comparison_dir, exist_ok=True)
        
        self.logger.info(f"DataLogger initialized with log directory: {self.log_dir}")
    
    def log_validation_results(self, validation_results, timestamp=None):
        """
        Log validation results for all commodities.

        Args:
            validation_results (dict): Validation results from DataValidator
            timestamp (datetime, optional): Timestamp for the log. Defaults to current time.
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.validation_dir, f"validation_{timestamp_str}.json")

        # Make results JSON serializable and add timestamp
        serializable_results = make_json_serializable(validation_results)
        results_with_timestamp = {
            "timestamp": timestamp.isoformat(),
            "results": serializable_results
        }

        with open(filename, 'w') as f:
            json.dump(results_with_timestamp, f, indent=2, cls=CustomJSONEncoder)
            
        self.logger.info(f"Validation results logged to {filename}")
        
        # Create a summary log entry
        summary = self._create_validation_summary(validation_results)
        summary_filename = os.path.join(self.validation_dir, "validation_summary.csv")
        
        # Check if summary file exists
        file_exists = os.path.isfile(summary_filename)
        
        with open(summary_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Total Commodities", "Valid Count", 
                    "Invalid Count", "Issues"
                ])
                
            writer.writerow([
                timestamp.isoformat(),
                summary["total_commodities"],
                summary["valid_count"],
                summary["invalid_count"],
                summary["issues_summary"]
            ])
    
    def _create_validation_summary(self, validation_results):
        """
        Create a summary of validation results.
        
        Args:
            validation_results (dict): Validation results
            
        Returns:
            dict: Summary statistics
        """
        total = len(validation_results)
        valid_count = sum(1 for result in validation_results.values() if result['valid'])
        invalid_count = total - valid_count
        
        # Create a summary of issues
        issues = {}
        for commodity, result in validation_results.items():
            if not result['valid']:
                for issue in result['issues']:
                    if issue not in issues:
                        issues[issue] = 0
                    issues[issue] += 1
        
        issues_summary = ", ".join([f"{issue} ({count})" for issue, count in issues.items()])
        
        return {
            "total_commodities": total,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "issues_summary": issues_summary
        }
    
    def capture_data_snapshot(self, data_dict, filters=None, timestamp=None):
        """
        Capture a snapshot of the commodity data.
        
        Args:
            data_dict (dict): Dictionary of commodity name to DataFrame
            filters (dict, optional): Filter settings applied to the data
            timestamp (datetime, optional): Timestamp for the snapshot
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create directory for this snapshot
        snapshot_dir = os.path.join(self.data_capture_dir, timestamp_str)
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Save filters if provided
        if filters:
            filter_file = os.path.join(snapshot_dir, "filters.json")
            with open(filter_file, 'w') as f:
                json.dump({
                    "timestamp": timestamp.isoformat(),
                    "filters": make_json_serializable(filters)
                }, f, indent=2, cls=CustomJSONEncoder)
        
        # Save each commodity DataFrame as CSV
        for commodity_name, df in data_dict.items():
            # Create safe filename
            safe_name = commodity_name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
            file_path = os.path.join(snapshot_dir, f"{safe_name}.csv")
            
            # Save to CSV
            df.to_csv(file_path, index=False)
            
        self.logger.info(f"Data snapshot captured to {snapshot_dir}")
        
        # Create snapshot entry in index
        index_file = os.path.join(self.data_capture_dir, "snapshots_index.csv")
        file_exists = os.path.isfile(index_file)
        
        with open(index_file, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Commodities Count", "Filters", "Directory"
                ])
                
            writer.writerow([
                timestamp.isoformat(),
                len(data_dict),
                str(filters) if filters else "None",
                snapshot_dir
            ])
    
    def log_price_comparison(self, commodity_name, current_price, previous_prices, timestamp=None):
        """
        Log price comparison for a specific commodity.

        Args:
            commodity_name (str): Name of the commodity
            current_price (float): Current price (might be a numpy type)
            previous_prices (dict): Dictionary of previous prices with timestamp keys
            timestamp (datetime, optional): Timestamp for the log
        """
        # Convert any numpy types to native Python types
        if isinstance(current_price, (np.integer, np.floating)):
            current_price = float(current_price)

        # Make previous_prices serializable
        previous_prices = make_json_serializable(previous_prices)
        if timestamp is None:
            timestamp = datetime.now()
            
        # Create safe filename
        safe_name = commodity_name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
        file_path = os.path.join(self.comparison_dir, f"{safe_name}_comparison.csv")
        
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Current Price", "1D Price", "1W Price", 
                    "1M Price", "1Y Price", "YTD Price"
                ])
                
            writer.writerow([
                timestamp.isoformat(),
                current_price,
                previous_prices.get("1d", ""),
                previous_prices.get("1w", ""),
                previous_prices.get("1m", ""),
                previous_prices.get("1y", ""),
                previous_prices.get("ytd", "")
            ])
            
        self.logger.info(f"Price comparison logged for {commodity_name}")
    
    def generate_data_quality_report(self):
        """
        Generate a simple HTML data quality report that can be downloaded from the browser.

        Returns:
            str: HTML content of the report
        """
        # Get summary metrics
        summary_data = []
        validation_summary_path = os.path.join(self.validation_dir, "validation_summary.csv")

        if os.path.exists(validation_summary_path):
            try:
                # Try to read validation summary if it exists
                summary_df = pd.read_csv(validation_summary_path)
                if not summary_df.empty:
                    last_row = summary_df.iloc[-1]
                    summary_data.append(("Total Commodities", last_row.get("Total Commodities", "N/A")))
                    summary_data.append(("Valid Commodities", last_row.get("Valid Count", "N/A")))
                    summary_data.append(("Commodities with Issues", last_row.get("Invalid Count", "N/A")))
                    summary_data.append(("Common Issues", last_row.get("Issues", "None found")))
            except Exception as e:
                self.logger.error(f"Error reading validation summary: {str(e)}")

        # Count snapshots
        snapshot_count = 0
        if os.path.exists(self.data_capture_dir):
            snapshot_count = len([d for d in os.listdir(self.data_capture_dir)
                              if os.path.isdir(os.path.join(self.data_capture_dir, d))])

        summary_data.append(("Data Snapshots Captured", snapshot_count))

        # Generate a simple HTML report
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
        <h2>Data Validation</h2>
        <p>This report provides a high-level overview of data quality for commodity price data.</p>
        <p>More detailed analysis and plots would be available in a full report implementation.</p>
    </div>

    <div class="section">
        <h2>Data Logging Status</h2>
        <p>The dashboard is configured to log:</p>
        <ul>
            <li>Data validation results</li>
            <li>Commodity price data snapshots</li>
            <li>Price change comparisons over time</li>
        </ul>
        <p>These logs are stored in the logs directory for future analysis.</p>
    </div>
</body>
</html>
"""

        self.logger.info("Data quality report generated for browser download")
        return html_content