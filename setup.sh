#!/bin/bash
# Setup script for Teck Resources Commodity Price Dashboard

# Exit on error
set -e

echo "Setting up Teck Resources Commodity Price Dashboard..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Bloomberg API (xbbg) is installed correctly
if python -c "import xbbg" &> /dev/null; then
    echo "Bloomberg API (xbbg) is installed correctly."
else
    echo "WARNING: Bloomberg API (xbbg) could not be imported. Make sure your Bloomberg environment is properly configured."
fi

echo "Setup complete! Use 'source venv/bin/activate' to activate the virtual environment."
echo "Run 'python run.py' to start the dashboard."