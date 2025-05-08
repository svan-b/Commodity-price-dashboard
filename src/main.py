"""
Main application entry point for Teck Resources Commodity Dashboard.
"""

import sys
import os
from ui.dashboard import Dashboard

def main():
    """Run the dashboard application."""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()