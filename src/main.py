"""
Main application entry point for Teck Resources Commodity Dashboard.
"""

import sys
import os
import warnings
import pandas as pd

# Filter the pandas is_sparse deprecation warning
warnings.filterwarnings(
    "ignore",
    message="is_sparse is deprecated and will be removed in a future version.",
    category=FutureWarning
)

from ui.dashboard import Dashboard

def main():
    """Run the dashboard application."""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()