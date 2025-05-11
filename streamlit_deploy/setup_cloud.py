"""
Setup script to ensure directory structure exists for Streamlit Cloud.
"""

import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        "logs",
        "logs/validation",
        "logs/data_capture",
        "logs/comparison",
        ".streamlit"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

if __name__ == "__main__":
    logger.info("Setting up directory structure for Streamlit Cloud")
    ensure_directories()
    logger.info("Setup complete")