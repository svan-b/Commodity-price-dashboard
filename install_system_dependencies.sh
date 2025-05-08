#!/bin/bash
# Script to install necessary dependencies without a virtual environment

echo "Installing dependencies for Teck Resources Commodity Price Dashboard..."

# Install pip dependencies
pip3 install -r requirements.txt

echo "Checking if xbbg (Bloomberg API) is installed..."
if python3 -c "import xbbg" &> /dev/null; then
    echo "Bloomberg API (xbbg) is installed correctly."
else
    echo "WARNING: Bloomberg API (xbbg) could not be imported."
    echo "Installing xbbg now..."
    pip3 install xbbg
    
    if python3 -c "import xbbg" &> /dev/null; then
        echo "Bloomberg API (xbbg) installed successfully."
    else
        echo "ERROR: Failed to install xbbg. Make sure your Bloomberg environment is properly configured."
    fi
fi

echo "Installation complete!"
echo "Run 'python3 run_without_venv.py' to start the dashboard."