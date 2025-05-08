# Teck Resources Commodity Price Dashboard

A real-time commodity price tracking dashboard for strategic decision making at Teck Resources.

## Features

- Real-time commodity price data from Bloomberg
- Interactive visualizations with price history and trends
- Categorized view of commodities by business importance
- Customizable timeframes and data frequencies
- Data validation and quality reporting
- Teck Resources branded design

## Project Structure
```
├── assets/               # Static assets (images, etc.)
├── src/                  # Source code
│   ├── data/             # Data access and validation
│   │   ├── bloomberg_api.py   # Bloomberg API integration
│   │   └── data_validator.py  # Data quality validation
│   ├── ui/               # User interface
│   │   └── dashboard.py  # Streamlit dashboard
│   ├── utils/            # Utility functions
│   │   └── helpers.py    # Formatting and helper utilities
│   ├── config.py         # Configuration settings
│   └── main.py           # Application entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/svan-b/commodity-price-dashboard.git
cd commodity-price-dashboard
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure you have Bloomberg API access configured on your machine.

## Running the Dashboard

To start the dashboard:

```bash
streamlit run src/main.py
```

The dashboard will be available at `http://localhost:8501` in your web browser.

## Author

Developed by [svan-b](https://github.com/svan-b)

## License

This project is proprietary and confidential to Teck Resources.