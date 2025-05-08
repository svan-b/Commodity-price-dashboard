# Teck Resources Commodity Price Dashboard

A professional dashboard for monitoring commodity prices with Bloomberg API integration, designed for Teck Resources' Market Research and Economic Analysis team.

## Features

- **Real-time commodity price monitoring** with Bloomberg API integration
- **Interactive visualizations** for price trends and comparisons
- **Logical grouping of commodities** by metal types (base metals, precious metals, energy, etc.)
- **Clear indicators** for spot vs futures prices
- **Data validation and quality checks** for reliable information
- **API status monitoring** with detailed metrics
- **Sample data generation** for testing without Bloomberg access
- **Responsive UI** with Teck Resources branding

## Project Structure

```
Commodity-price-dashboard/
├── assets/                  # Static assets
├── src/                     # Source code
│   ├── config/              # Configuration files
│   ├── data/                # Data retrieval and validation
│   │   ├── bloomberg_api.py # Bloomberg API integration
│   │   └── data_validator.py # Data validation module
│   ├── ui/                  # User interface components
│   │   └── dashboard.py     # Streamlit dashboard implementation
│   ├── utils/               # Utility functions
│   │   └── helpers.py       # Helper functions for formatting, etc.
│   ├── visualization/       # Visualization components
│   ├── config.py            # Main configuration
│   └── main.py              # Application entry point
├── requirements.txt         # Python dependencies
├── run.py                   # Script to run the dashboard
└── README.md                # Project documentation
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

## Usage

### Running the Dashboard

To run the dashboard:

```bash
python run.py
```

Or directly with Streamlit:

```bash
streamlit run src/main.py
```

The dashboard will be available at `http://localhost:8501` in your web browser.

### Dashboard Features

1. **Price Cards View**: Quick overview of all commodity prices with color indicators
2. **Market Overview**: Comparative price trends across commodities
3. **Detailed Analysis**: Individual commodity price charts and metrics
4. **API Status**: Data validation metrics and Bloomberg connection status

### Configuration

Edit `src/config.py` to customize:

- Commodities and their groupings
- Bloomberg tickers
- UI settings and colors
- Default timeframes and frequencies

## Cloud Deployment

### Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Select `src/main.py` as the entry point
5. Configure any necessary secrets for Bloomberg API

### Deploying to Heroku

1. Create a `Procfile` with:
   ```
   web: streamlit run src/main.py --server.port $PORT
   ```
2. Create a `runtime.txt` with:
   ```
   python-3.9.0
   ```
3. Push to Heroku:
   ```bash
   heroku create teck-commodity-dashboard
   git push heroku master
   ```

## Author

Developed by [svan-b](https://github.com/svan-b) for Teck Resources' Market Research and Economic Analysis team.

## License

This project is proprietary and confidential to Teck Resources.