# Testing and Running the Teck Resources Commodity Price Dashboard

This document provides instructions for setting up, testing, and running the commodity price dashboard.

## Prerequisites

- Python 3.8 or higher
- Bloomberg Terminal (for live data) or sample data will be used

## Installation

### Option 1: System-wide Installation

Run the installation script:

```bash
./install_system_dependencies.sh
```

This will install all required Python packages.

### Option 2: Virtual Environment (Recommended)

If you have Python's venv module available:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Testing Bloomberg API Connectivity

Before running the full dashboard, you can test if your Bloomberg API connectivity is working:

```bash
python3 test_bloomberg.py
```

This script will:
1. Test if xbbg is installed
2. Attempt to fetch some simple data from Bloomberg
3. Report if the connection is working

If you don't have Bloomberg access, the dashboard will still work with sample data.

## Running the Dashboard

### Using the run script:

```bash
# If using system installation
python3 run_without_venv.py

# If using virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

### Direct Streamlit command:

```bash
# If using system installation
streamlit run src/main.py

# If using virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
streamlit run src/main.py
```

## UI Verification

When the dashboard loads, verify:

1. **Data Loading**: Check if commodity data loads either from Bloomberg or sample data
2. **Error Handling**: Empty states are handled gracefully with informative messages
3. **Filtering**: Date range, frequency, and commodity filters work as expected
4. **Visualizations**: Charts and cards display correctly with proper formatting
5. **Interactivity**: Tabs and interactive elements respond to user actions

## Troubleshooting

### Bloomberg API Issues

- Ensure Bloomberg Terminal is running
- Check if xbbg is properly installed (`pip show xbbg`)
- Verify Bloomberg tickers in config.py

### Display Issues

- If charts don't render, check browser console for errors
- Streamlit has compatibility issues with some older browsers

### Performance Issues

- Reducing the date range and number of commodities will improve performance
- Monthly data frequency requires less processing than daily data