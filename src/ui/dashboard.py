"""
Streamlit dashboard UI for commodity price visualization.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import logging
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TECK_BLUE, COPPER_ORANGE, BACKGROUND_WHITE, TEXT_COLOR,
    DASHBOARD_TITLE, DASHBOARD_SUBTITLE,
    DEFAULT_TIMEFRAME, DEFAULT_DATA_FREQUENCY,
    AVAILABLE_TIMEFRAMES, AVAILABLE_FREQUENCIES,
    CATEGORIES, COMMODITIES
)
from utils.data_logger import DataLogger
from data.bloomberg_api import BloombergAPI
from data.data_validator import DataValidator
from utils.helpers import (
    format_price, calculate_change, create_price_chart,
    create_multi_commodity_chart, get_data_update_text,
    format_change_value
)

class Dashboard:
    """Streamlit dashboard for commodity price visualization."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.bloomberg_api = BloombergAPI()
        self.data_validator = DataValidator()
        self.data_logger = DataLogger(log_dir="logs")
        self.configure_page()
        
    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=DASHBOARD_TITLE,
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Force light mode theme
        st.markdown("""
        <script>
            localStorage.setItem('color-theme', 'light');
            localStorage.setItem('streamlit_theming', '{"base":"light"}');
        </script>
        """, unsafe_allow_html=True)
        
        # Apply custom CSS for a more professional look
        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 16px;
        }}
        
        .main .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 1800px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {TECK_BLUE};
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        
        h1 {{
            font-size: 2.2rem;
            font-weight: 700;
        }}
        
        h2 {{
            font-size: 1.8rem;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
            margin-top: 1.5rem;
        }}
        
        h3 {{
            font-size: 1.3rem;
            font-weight: 600;
        }}
        
        p, div, span, label {{
            font-size: 1.1rem;
        }}
        
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
            font-size: 1rem;
            font-weight: 500;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}
        
        .stTabs [data-baseweb="tab-list"] button {{
            background-color: #f8f9fa;
            border-radius: 4px 4px 0 0;
            border: 1px solid #eaecef;
            border-bottom: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }}
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
            background-color: {TECK_BLUE};
            color: white;
            border: 1px solid {TECK_BLUE};
            border-bottom: none;
        }}
        
        .stTabs [data-baseweb="tab-panel"] {{
            padding: 1rem;
            border: 1px solid #eaecef;
            border-top: none;
            border-radius: 0 0 4px 4px;
        }}
        
        .data-update-text {{
            font-size: 0.8rem;
            color: #6c757d;
            font-style: italic;
            margin-top: 0.5rem;
        }}
        
        .teck-header {{
            background-color: {TECK_BLUE};
            padding: 2rem;
            color: white;
            border-radius: 5px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .teck-logo {{
            font-weight: 800;
            font-size: 2.5rem;
            letter-spacing: -0.03em;
            margin-right: 2rem;
            border-right: 2px solid rgba(255,255,255,0.3);
            padding-right: 2rem;
            line-height: 1;
        }}
        
        .teck-header-content {{
            flex: 1;
        }}
        
        .teck-header-content h1 {{
            color: white;
            margin-bottom: 0.3rem;
            font-size: 1.8rem;
        }}
        
        .teck-header-content p {{
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            margin: 0;
        }}

        .teck-header-info {{
            font-size: 0.9rem;
            color: rgba(255,255,255,0.8);
            margin-left: auto;
            padding-left: 2rem;
        }}

        .dashboard-info-bar {{
            display: flex;
            background-color: #f8f9fa;
            border-radius: 0 0 5px 5px;
            padding: 0.6rem 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-size: 0.85rem;
            color: #555;
            justify-content: space-between;
        }}

        .info-label {{
            font-weight: 600;
            color: #00103f;
            margin-right: 0.3rem;
        }}

        .info-tooltip {{
            cursor: help;
        }}

        .price-card {{
            border: 1px solid #eaecef;
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            background-color: {BACKGROUND_WHITE};
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            overflow: hidden;
        }}
        
        .price-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .color-indicator {{
            position: absolute;
            top: 0;
            right: 0;
            width: 35px;
            height: 35px;
            border-radius: 0 8px 0 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            opacity: 0.9;
        }}
        
        .price-card h3 {{
            margin-top: 0;
            color: {TECK_BLUE};
            font-size: 1.3rem;
            font-weight: 600;
            border-bottom: none;
            padding-bottom: 0;
            margin-right: 25px; /* Space for color indicator */
            margin-bottom: 0.8rem;
        }}
        
        .price-value {{
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0.7rem 0;
            letter-spacing: -0.01em;
        }}
        
        .price-change {{
            padding: 0.2rem 0rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 0.8rem;
            font-size: 1.1rem;
        }}

        .price-change:hover {{
            text-decoration: underline;
        }}

        .price-change.positive {{
            color: #28a745;
        }}

        .price-change.negative {{
            color: #dc3545;
        }}

        .price-change.neutral {{
            color: #6c757d;
        }}
        
        .price-units {{
            color: #6c757d;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .data-source {{
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 0.7rem;
            border-top: 1px solid #f5f5f5;
            padding-top: 0.7rem;
        }}
        
        .price-type {{
            font-weight: 600;
        }}
        
        /* Sidebar styling */
        .css-1cypcdb, .css-10oheav {{
            background-color: #f8f9fa !important;
        }}
        
        .stSelectbox label {{
            font-weight: 500;
            color: #343a40;
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {TECK_BLUE};
            color: white;
            border: none;
            padding: 0.4rem 1rem;
            font-weight: 500;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .stButton > button:hover {{
            background-color: #003366;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        /* Plotly chart styling */
        .js-plotly-plot {{
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            background-color: white;
            padding: 1rem;
        }}
        
        footer {{
            margin-top: 2rem;
            text-align: center;
            font-size: 0.8rem;
            color: #6c757d;
            padding: 1rem;
            border-top: 1px solid #eaecef;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Render dashboard header."""
        st.markdown(f"""
        <div class="teck-header">
            <div class="teck-logo">TECK</div>
            <div class="teck-header-content">
                <h1>{DASHBOARD_TITLE}</h1>
                <p>Market Research and Economic Analysis</p>
            </div>
            <div class="teck-header-info">
                <p>Last updated: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </div>

        <div class="dashboard-info-bar">
            <div>
                <span class="info-label">Data source:</span> Bloomberg Terminal API & Sample Data
            </div>
            <div>
                <span class="info-label">Timeframe controls:</span> Use the sidebar to adjust display settings
            </div>
            <div>
                <span class="info-label" title="Prices marked with an asterisk (*) share reference points due to limited data">Help:</span>
                <span class="info-tooltip">Hover over charts for details</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_filters(self):
        """Render sidebar filters."""
        st.sidebar.title("Dashboard Controls")

        # Add instructions at the top of the sidebar
        st.sidebar.markdown("""
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 0.9rem;">
            <p style="font-weight: bold; margin-bottom: 5px;">📊 How to use this dashboard:</p>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Select a timeframe to view data over different periods</li>
                <li>Choose data frequency from daily, weekly, or monthly</li>
                <li>Select specific commodities to analyze</li>
                <li>Use tabs to switch between different views</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Timeframe filter
        timeframe = st.sidebar.selectbox(
            "Timeframe",
            options=AVAILABLE_TIMEFRAMES,
            index=AVAILABLE_TIMEFRAMES.index(DEFAULT_TIMEFRAME)
        )
        
        # Calculate start date based on timeframe
        end_date = datetime.now()
        if timeframe == "1M":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "3M":
            start_date = end_date - timedelta(days=90)
        elif timeframe == "6M":
            start_date = end_date - timedelta(days=180)
        elif timeframe == "1Y":
            start_date = end_date - timedelta(days=365)
        elif timeframe == "5Y":
            start_date = end_date - timedelta(days=1825)
        else:
            start_date = end_date - timedelta(days=365)  # Default to 1Y
            
        # Convert to string format
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Data frequency filter
        frequency = st.sidebar.selectbox(
            "Data Frequency",
            options=AVAILABLE_FREQUENCIES,
            index=AVAILABLE_FREQUENCIES.index(DEFAULT_DATA_FREQUENCY)
        )
        
        # Group commodities by category for the multiselect
        grouped_commodities = {}
        for category_name, category_display in CATEGORIES.items():
            commodities_in_category = [c["name"] for c in COMMODITIES if c["category"] == category_name]
            if commodities_in_category:
                grouped_commodities[f"{category_display}"] = commodities_in_category
        
        # Create a list of all commodities
        all_commodities = []
        for category_commodities in grouped_commodities.values():
            all_commodities.extend(category_commodities)
            
        # Commodity multiselect with all commodities
        selected_commodities = st.sidebar.multiselect(
            "Select Commodities",
            options=all_commodities,
            default=all_commodities  # Default to all commodities
        )
        
        # Add a select all button
        if st.sidebar.button("Select All Commodities"):
            selected_commodities = all_commodities
        
        # Infer category from selections - use "all" if commodities from multiple categories
        categories = set()
        for commodity in COMMODITIES:
            if commodity["name"] in selected_commodities:
                categories.add(commodity["category"])
        
        category = list(categories)[0] if len(categories) == 1 else "all"
        
        return {
            "timeframe": timeframe,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "frequency": frequency,
            "category": category,
            "selected_commodities": selected_commodities
        }
    
    def load_data(self, filters, full_history=False):
        """
        Load commodity data based on filters.

        Args:
            filters (dict): Filter settings
            full_history (bool): If True, fetches maximum available history regardless of filters

        Returns:
            dict: Dictionary of commodity data
        """
        data = {}

        # Get commodity data for selected commodities
        for commodity_name in filters["selected_commodities"]:
            # If full_history is requested, don't restrict date range
            if full_history:
                extended_start_date = None  # This will use the maximum history available
            else:
                # Request data for a longer period than needed, especially for monthly data
                # This ensures we have enough data points for historical comparison
                extended_start_date = filters["start_date"]

                # For monthly data, extend further back to allow better period calculations
                if filters["frequency"] == "monthly":
                    # Parse start date
                    start_date_obj = datetime.strptime(filters["start_date"], "%Y-%m-%d")
                    # Go back 2 years to ensure enough data points
                    extended_start_date_obj = start_date_obj - timedelta(days=365*2)
                    extended_start_date = extended_start_date_obj.strftime("%Y-%m-%d")
                # For weekly data, go back 6 months
                elif filters["frequency"] == "weekly":
                    start_date_obj = datetime.strptime(filters["start_date"], "%Y-%m-%d")
                    extended_start_date_obj = start_date_obj - timedelta(days=180)
                    extended_start_date = extended_start_date_obj.strftime("%Y-%m-%d")
                # For daily data, go back 1 month
                else:
                    start_date_obj = datetime.strptime(filters["start_date"], "%Y-%m-%d")
                    extended_start_date_obj = start_date_obj - timedelta(days=30)
                    extended_start_date = extended_start_date_obj.strftime("%Y-%m-%d")

            df = self.bloomberg_api.get_commodity_data(
                commodity_name,
                start_date=extended_start_date,
                end_date=filters["end_date"],
                freq=filters["frequency"]
            )

            if not df.empty:
                # Validate the data
                validation_result = self.data_validator.validate_dataframe(df, commodity_name)

                if validation_result['valid']:
                    # Store full dataset with extended history for proper change calculations
                    data[commodity_name] = df
                else:
                    # If validation fails, only log to console but not on main UI
                    issues = ', '.join(validation_result['issues'])
                    logging.warning(f"Data quality issues for {commodity_name}: {issues}")

                    # Still include the data but mark it as having issues
                    df['has_quality_issues'] = True
                    data[commodity_name] = df

                # Store latest price and historical prices for comparison logging
                if not df.empty and 'Price' in df.columns:
                    latest_price = df.iloc[-1]['Price'] if len(df) > 0 else None

                    # Get historical prices for comparison
                    historical_prices = {}

                    # Ensure df has required columns before calculating changes
                    if 'Date' in df.columns and 'Price' in df.columns and not df.empty:
                        period_changes = calculate_change(df)
                    else:
                        # Create default changes dict if dataframe is missing required columns
                        period_changes = {
                            'last_price': None,
                            'previous_price': None,
                            'change_1d': None,
                            'change_1d_pct': None,
                            'change_1w': None,
                            'change_1w_pct': None,
                            'change_1m': None,
                            'change_1m_pct': None,
                            'change_1y': None,
                            'change_1y_pct': None,
                            'change_ytd': None,
                            'change_ytd_pct': None
                        }

                    # Extract historical prices from changes
                    for period in ['1d', '1w', '1m', '1y', 'ytd']:
                        if f'change_{period}_date' in period_changes and period_changes[f'change_{period}_date'] is not None:
                            historical_date = period_changes[f'change_{period}_date']
                            historical_df = df[df['Date'] == historical_date]
                            if not historical_df.empty:
                                historical_prices[period] = historical_df.iloc[0]['Price']

                    # Log price comparison
                    self.data_logger.log_price_comparison(
                        commodity_name,
                        latest_price,
                        historical_prices
                    )

        return data
    
    def render_overview_tab(self, data, filters):
        """
        Render the overview tab with summary charts.
        
        Args:
            data (dict): Dictionary of commodity data
            filters (dict): Filter settings
        """
        if not data:
            st.warning("No data available for the selected filters.")
            return
            
        # Handle 'all' category case
        if filters['category'] == 'all':
            st.subheader("Market Overview - All Selected Commodities")
        else:
            st.subheader(f"{CATEGORIES[filters['category']]} - Overview")
        
        # Create normalized comparison chart
        comparison_chart = create_multi_commodity_chart(data, filters["category"])
        st.plotly_chart(comparison_chart, use_container_width=True)
        
        # Last updated info
        update_dates = [df["Date"].max() for df in data.values() if not df.empty]
        if update_dates:
            latest_update = max(update_dates)
            latest_update_str = latest_update.strftime("%B %d, %Y")
            days_ago = (datetime.now() - latest_update).days
            
            if days_ago == 0:
                days_text = "today"
            elif days_ago == 1:
                days_text = "yesterday"
            else:
                days_text = f"{days_ago} days ago"
                
            st.markdown(f"""
            <div class="data-update-text">
                Data last updated: {latest_update_str} ({days_text})
            </div>
            """, unsafe_allow_html=True)
            
        # Data validation summary
        validation_results = self.data_validator.validate_all_data(data)
        validation_summary = self.data_validator.get_validation_summary(validation_results)
        
        with st.expander("Data Quality Information"):
            st.write(f"**Total Commodities:** {validation_summary['total_commodities']}")
            st.write(f"**Commodities with Valid Data:** {validation_summary['valid_commodities']}")
            
            if validation_summary['commodities_with_issues'] > 0:
                st.write(f"**Commodities with Issues:** {validation_summary['commodities_with_issues']}")
                for commodity, issues in validation_summary['issue_details'].items():
                    st.write(f"- **{commodity}:** {', '.join(issues)}")
    
    def render_commodity_cards(self, data, filters):
        """
        Render individual commodity cards.
        
        Args:
            data (dict): Dictionary of commodity data
            filters (dict): Filter settings
        """
        if not data:
            st.warning("No data available for the selected filters.")
            return
        
        # Group commodities by category
        commodity_by_category = {}
        
        # Get the complete commodity info for each loaded commodity
        commodity_info = {}
        for commodity in COMMODITIES:
            commodity_info[commodity['name']] = commodity
            
        # Group by category
        for commodity_name, df in data.items():
            if df.empty:
                continue
                
            if commodity_name in commodity_info:
                category = commodity_info[commodity_name]['category']
                if category not in commodity_by_category:
                    commodity_by_category[category] = []
                commodity_by_category[category].append((commodity_name, df, commodity_info[commodity_name]))
        
        # Define the category display order
        category_order = ['base_metals', 'precious_metals', 'rare_metals', 'energy', 'steel_materials']
        
        # Render cards in specific category order
        for category in category_order:
            if category not in commodity_by_category or not commodity_by_category[category]:
                continue
                
            # Add category header
            st.markdown(f"## {CATEGORIES[category]}")
            
            # Create four-column layout for each category
            cols = st.columns(4)
            col_idx = 0
            
            for commodity_name, df, commodity_info in commodity_by_category[category]:
                # Get metadata
                units = df["Units"].iloc[0] if "Units" in df.columns else "N/A"
                data_source = df["Data Source"].iloc[0] if "Data Source" in df.columns else "N/A"
                ticker = df["Ticker"].iloc[0] if "Ticker" in df.columns else "N/A"
                commodity_type = df["Type"].iloc[0] if "Type" in df.columns else "N/A"
                color = commodity_info.get('color', '#CCCCCC')  # Default to gray if no color specified
                
                # Calculate changes
                changes = calculate_change(df)
                
                # Format last price
                last_price = changes['last_price']
                formatted_price = format_price(last_price, units) if last_price is not None else "N/A"
                
                # Format changes - handle old and new format changes dictionary
                if 'change_1d' in changes:
                    # New format with detailed changes
                    change_text, change_color = format_change_value(
                        changes['change_1d'], changes['change_1d_pct'],
                        changes.get('change_1d_is_duplicate', False)
                    )
                else:
                    # Original format
                    change_text, change_color = format_change_value(
                        changes.get('change_recent', 0), changes.get('change_recent_pct', 0)
                    )
                
                # Select column to render in
                col = cols[col_idx % 4]
                col_idx += 1
                
                with col:
                    # Render commodity card with color block and price type indicator
                    price_type_indicator = "SPOT" if "Spot" in commodity_type else "FUTURES"
                    price_type_color = "#000000" if "Spot" in commodity_type else "#b0350b"  # Black for spot, red for futures
                    
                    # Determine appropriate change period text based on data frequency
                    # If we have few data points or large gaps, it's likely monthly data
                    date_diffs = [(df['Date'].iloc[i] - df['Date'].iloc[i-1]).days 
                                 for i in range(1, min(4, len(df)))] if len(df) > 1 else [30]
                    avg_diff = sum(date_diffs) / len(date_diffs)
                    
                    if avg_diff < 2:
                        change_period = "1-Day Change"
                    elif avg_diff < 10:
                        change_period = "Weekly Change"
                    else:
                        change_period = "Monthly Change"
                    
                    # Check if the change_text contains an asterisk
                    asterisk_tooltip = ""
                    if "*" in change_text:
                        asterisk_tooltip = 'title="* Limited data available; some periods are using reference points based on available data"'

                    # Get the last price date
                    last_date = df['Date'].max().strftime('%Y-%m-%d') if not df.empty else "N/A"

                    col.markdown(f"""
                    <div class="price-card">
                        <div class="color-indicator" style="background-color: {color};"></div>
                        <div style="position: absolute; top: 10px; right: 40px; font-size: 0.7rem; font-weight: bold; color: {price_type_color}; background-color: rgba(0,0,0,0.05); padding: 2px 8px; border-radius: 3px;">{price_type_indicator}</div>
                        <h3>{commodity_name}</h3>
                        <div class="price-value">{formatted_price}</div>
                        <div class="price-change {change_color}" {asterisk_tooltip}>{change_text}</div>
                        <div style="font-size: 0.75rem; color: #6c757d; margin-top: -5px; margin-bottom: 5px;">
                            <strong>{change_period}</strong> • As of {last_date}
                        </div>
                        <div class="price-units">{units}</div>
                        <div class="data-source">
                            <span class="price-type">{commodity_type}</span> | {data_source} | {ticker}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def render_individual_tabs(self, data, filters):
        """
        Render individual tabs for each commodity.

        Args:
            data (dict): Dictionary of commodity data
            filters (dict): Filter settings
        """
        if not data:
            st.warning("No data available for the selected filters.")
            return

        # Use selectbox for better navigation instead of tabs
        # This ensures you can always go back to earlier commodities
        commodities = list(data.keys())
        selected_commodity = st.selectbox("Select Commodity", commodities)

        # Toggle for showing full history
        show_full_history = st.checkbox("Show Full Price History", value=True)

        if show_full_history:
            # Load full history data for this commodity
            full_data = {}
            full_data[selected_commodity] = self.bloomberg_api.get_commodity_data(
                selected_commodity,
                start_date=None,  # Using None will fetch max available history
                end_date=None,
                freq=filters["frequency"]
            )
            # Use the full history data instead
            df = full_data[selected_commodity]
        else:
            # Use the filtered data
            df = data[selected_commodity]

        # Display the selected commodity's data
        if df.empty:
            st.warning(f"No data available for {selected_commodity}.")
            return

        # Get metadata
        units = df["Units"].iloc[0] if "Units" in df.columns else "N/A"
        data_source = df["Data Source"].iloc[0] if "Data Source" in df.columns else "N/A"
        ticker = df["Ticker"].iloc[0] if "Ticker" in df.columns else "N/A"
        commodity_type = df["Type"].iloc[0] if "Type" in df.columns else "N/A"

        # Create two columns
        col1, col2 = st.columns([3, 1])

        with col1:
            # Price chart
            chart = create_price_chart(df, selected_commodity, units)
            st.plotly_chart(chart, use_container_width=True)

            # Last updated info
            st.markdown(f"""
            <div class="data-update-text">
                {get_data_update_text(df)}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Price information
            changes = calculate_change(df)

            # Format last price
            last_price = changes['last_price']
            formatted_price = format_price(last_price, units) if last_price is not None else "N/A"

            st.markdown(f"### Current Price")
            st.markdown(f"<div class='price-value'>{formatted_price}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='price-units'>{units} • {commodity_type}</div>", unsafe_allow_html=True)

            # Price changes
            st.markdown("### Price Changes")

            # Always use the detailed changes format
            if 'change_1d' in changes:
                # New format with detailed changes
                change_1d_text, change_1d_color = format_change_value(
                    changes['change_1d'], changes['change_1d_pct'],
                    changes.get('change_1d_is_duplicate', False)
                )
                change_1w_text, change_1w_color = format_change_value(
                    changes['change_1w'], changes['change_1w_pct'],
                    changes.get('change_1w_is_duplicate', False)
                )
                change_1m_text, change_1m_color = format_change_value(
                    changes['change_1m'], changes['change_1m_pct'],
                    changes.get('change_1m_is_duplicate', False)
                )
                change_1y_text, change_1y_color = format_change_value(
                    changes['change_1y'], changes['change_1y_pct'],
                    changes.get('change_1y_is_duplicate', False)
                )
                change_ytd_text, change_ytd_color = format_change_value(
                    changes['change_ytd'], changes['change_ytd_pct'],
                    changes.get('change_ytd_is_duplicate', False)
                )

                # Include reference dates in tooltips for transparency
                # Only show if available in the change data - handle case where date might be None
                date_1d = "Reference date: N/A"
                if 'change_1d_date' in changes and changes.get('change_1d_date') is not None:
                    date_1d = f"Reference date: {changes.get('change_1d_date').strftime('%Y-%m-%d')}"

                date_1w = "Reference date: N/A"
                if 'change_1w_date' in changes and changes.get('change_1w_date') is not None:
                    date_1w = f"Reference date: {changes.get('change_1w_date').strftime('%Y-%m-%d')}"

                date_1m = "Reference date: N/A"
                if 'change_1m_date' in changes and changes.get('change_1m_date') is not None:
                    date_1m = f"Reference date: {changes.get('change_1m_date').strftime('%Y-%m-%d')}"

                date_1y = "Reference date: N/A"
                if 'change_1y_date' in changes and changes.get('change_1y_date') is not None:
                    date_1y = f"Reference date: {changes.get('change_1y_date').strftime('%Y-%m-%d')}"

                date_ytd = "Reference date: N/A"
                if 'change_ytd_date' in changes and changes.get('change_ytd_date') is not None:
                    date_ytd = f"Reference date: {changes.get('change_ytd_date').strftime('%Y-%m-%d')}"

                # Check for instances where periods share reference points
                has_duplicate = any(changes.get(f'change_{period}_is_duplicate', False)
                                   for period in ['1d', '1w', '1m', '1y', 'ytd'])
            else:
                # Fallback for older data format - should not happen after our updates
                recent_change = changes.get('change_recent', 0)
                recent_change_pct = changes.get('change_recent_pct', 0)

                # Use the same change for all periods as fallback
                change_1d_text, change_1d_color = format_change_value(recent_change, recent_change_pct, True)
                change_1w_text, change_1w_color = format_change_value(recent_change, recent_change_pct, True)
                change_1m_text, change_1m_color = format_change_value(recent_change, recent_change_pct, True)
                change_1y_text, change_1y_color = format_change_value(recent_change, recent_change_pct, True)
                change_ytd_text, change_ytd_color = format_change_value(recent_change, recent_change_pct, True)

                # No reference dates available
                date_1d = date_1w = date_1m = date_1y = date_ytd = "Reference date: N/A"
                has_duplicate = True

            # Add tooltips with reference dates for better data transparency
            change_table = f"""
            <table style="width:100%;">
              <tr>
                <th style="text-align:left; padding-bottom:8px;">Period</th>
                <th style="text-align:right; padding-bottom:8px;">Change</th>
              </tr>
              <tr title="{date_1d}">
                <td style="text-align:left; padding:4px 0;">1 Day</td>
                <td style="text-align:right; padding:4px 0; color:{change_1d_color};">{change_1d_text}</td>
              </tr>
              <tr title="{date_1w}">
                <td style="text-align:left; padding:4px 0;">1 Week</td>
                <td style="text-align:right; padding:4px 0; color:{change_1w_color};">{change_1w_text}</td>
              </tr>
              <tr title="{date_1m}">
                <td style="text-align:left; padding:4px 0;">1 Month</td>
                <td style="text-align:right; padding:4px 0; color:{change_1m_color};">{change_1m_text}</td>
              </tr>
              <tr title="{date_1y}">
                <td style="text-align:left; padding:4px 0;">1 Year</td>
                <td style="text-align:right; padding:4px 0; color:{change_1y_color};">{change_1y_text}</td>
              </tr>
              <tr title="{date_ytd}">
                <td style="text-align:left; padding:4px 0;">YTD</td>
                <td style="text-align:right; padding:4px 0; color:{change_ytd_color};">{change_ytd_text}</td>
              </tr>
            </table>
            """

            if has_duplicate:
                change_table += '<div style="font-size: 0.8rem; color: #888; margin-top: 8px;">* Limited data available; some periods are using reference points based on available data. Hover over rows to see reference dates.</div>'

            st.markdown(change_table, unsafe_allow_html=True)

            # Metadata
            st.markdown("### Metadata")
            st.markdown(f"""
            | Field | Value |
            | ----- | ----- |
            | Data Source | {data_source} |
            | Ticker | {ticker} |
            | Type | {commodity_type} |
            | Units | {units} |
            """)

        # Data table
        with st.expander("View Raw Data"):
            display_df = df[['Date', 'Price']].copy()
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.sort_values('Date', ascending=False)
            st.dataframe(display_df, use_container_width=True)
    
    def render_api_status_tab(self, data, filters):
        """
        Render API status and data validation information.
        
        Args:
            data (dict): Dictionary of commodity data
            filters (dict): Filter settings
        """
        st.markdown("## Bloomberg API Status")
        
        # Connection status indicator
        has_data = any(not df.empty for df in data.values())
        bloomberg_source = any(df["Data Source"].iloc[0] == "Bloomberg" for df in data.values() if not df.empty)
        
        connection_status = "Connected" if bloomberg_source else "Disconnected"
        connection_color = "green" if bloomberg_source else "red"
        
        st.markdown(f"""
        <div style="padding: 1rem; background-color: rgba(0,0,0,0.05); border-radius: 0.5rem; margin-bottom: 1rem;">
            <h3>Connection Status: <span style="color: {connection_color};">{connection_status}</span></h3>
            <p>Last connection attempt: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Data source: {"Bloomberg Terminal" if bloomberg_source else "Sample Data"}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get the validation results for the data
        validation_results = self.data_validator.validate_all_data(data)
        validation_summary = self.data_validator.get_validation_summary(validation_results)
        
        # Create columns for API status metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Commodities with Data", 
                f"{validation_summary['valid_commodities']} / {validation_summary['total_commodities']}",
                delta=None
            )
            
        with col2:
            if validation_summary['commodities_with_issues'] > 0:
                delta_color = "inverse"
            else:
                delta_color = "normal"
                
            st.metric(
                "Commodities with Issues", 
                validation_summary['commodities_with_issues'],
                delta=f"{validation_summary['commodities_with_issues']} issues",
                delta_color=delta_color
            )
            
        with col3:
            # Get the most recent timestamp across all data
            update_dates = [df["Date"].max() for df in data.values() if not df.empty]
            if update_dates:
                latest_update = max(update_dates)
                latest_update_str = latest_update.strftime("%B %d, %Y")
                days_ago = (datetime.now() - latest_update).days
                
                st.metric(
                    "Last Data Update", 
                    latest_update_str,
                    delta=f"{days_ago} days ago"
                )
            else:
                st.metric(
                    "Last Data Update", 
                    "N/A",
                    delta=None
                )
        
        # Display detailed data validation information
        st.markdown("## Data Validation Details")
        
        # Create an expandable section for each commodity
        for commodity_name, result in validation_results.items():
            # Find the commodity info
            commodity_info = next((c for c in COMMODITIES if c['name'] == commodity_name), None)
            
            # Get the last price value if available
            last_price = None
            last_date = None
            if commodity_name in data and not data[commodity_name].empty:
                df = data[commodity_name]
                last_price = df['Price'].iloc[-1] if not df.empty else None
                last_date = df['Date'].iloc[-1] if not df.empty else None
            
            # Format the status display
            if result['valid']:
                status_icon = "✅"
            else:
                status_icon = "⚠️"
                
            # Create the commodity description text
            description = "No description available"
            ticker_info = "No ticker information"
            if commodity_info:
                description = commodity_info.get('description', 'No description available')
                if commodity_info.get('preferred_ticker'):
                    ticker_info = f"Primary Ticker: {commodity_info['preferred_ticker']}"
                    if commodity_info.get('alternative_ticker'):
                        ticker_info += f" | Alternative: {commodity_info['alternative_ticker']}"
                elif commodity_info.get('alternative_ticker'):
                    ticker_info = f"Alternative Ticker: {commodity_info['alternative_ticker']}"
            
            # Last value display
            last_value_text = "No data available"
            if last_price is not None and last_date is not None:
                last_value_text = f"{format_price(last_price, commodity_info.get('units', 'N/A'))} on {last_date.strftime('%Y-%m-%d')}"
            
            with st.expander(f"{status_icon} {commodity_name}"):
                # Description and ticker info
                st.markdown(f"**Description**: {description}")
                st.markdown(f"**Ticker Information**: {ticker_info}")
                st.markdown(f"**Last Value**: {last_value_text}")
                
                if not result['valid']:
                    st.markdown("### Issues")
                    for issue in result['issues']:
                        st.markdown(f"- {issue}")
                
                # Display metrics if available
                if result['metrics']:
                    st.markdown("### Metrics")
                    
                    # Format date range nicely if available
                    metrics_display = {}
                    for k, v in result['metrics'].items():
                        if k == 'date_range' and isinstance(v, list) and len(v) == 2:
                            try:
                                metrics_display[k] = f"{v[0].strftime('%Y-%m-%d')} to {v[1].strftime('%Y-%m-%d')}"
                            except:
                                metrics_display[k] = str(v)
                        elif isinstance(v, float):
                            metrics_display[k] = f"{v:.2f}"
                        else:
                            metrics_display[k] = str(v)
                    
                    metrics_df = pd.DataFrame({
                        'Metric': list(metrics_display.keys()),
                        'Value': list(metrics_display.values())
                    })
                    st.dataframe(metrics_df)
        
        # Data Quality Reports
        st.markdown("## Data Quality Reports")

        # Add a button to generate a data quality report
        if st.button("Generate Data Quality Report"):
            with st.spinner("Generating data quality report..."):
                report_html = self.data_logger.generate_data_quality_report()
                # Create a download button for the report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Download Data Quality Report",
                    data=report_html,
                    file_name=f"commodity_data_quality_report_{timestamp}.html",
                    mime="text/html"
                )
                st.success("Data quality report generated successfully! Click the button above to download.")

        # Bloomberg API Configuration
        st.markdown("## Bloomberg API Configuration")

        # Display ticker configurations
        st.markdown("### Commodity Tickers")
        
        ticker_data = []
        for commodity in COMMODITIES:
            ticker_type = "Primary" if commodity['preferred_ticker'] else "Alternative"
            if commodity['preferred_ticker'] or commodity['alternative_ticker']:
                ticker = commodity['preferred_ticker'] or commodity['alternative_ticker']
                ticker_data.append({
                    "Commodity": commodity['name'],
                    "Category": CATEGORIES[commodity['category']],
                    "Ticker": ticker,
                    "Type": commodity['type'],
                    "Units": commodity['units']
                })
        
        ticker_df = pd.DataFrame(ticker_data)
        st.dataframe(ticker_df)
        
    def render_footer(self):
        """Render dashboard footer."""
        current_date = datetime.now().strftime('%B %d, %Y')
        st.markdown(f"""
        <footer>
            <div class="footer-content">
                <div class="footer-section">
                    <strong>Teck Resources Commodity Price Dashboard</strong><br>
                    Data retrieved via Bloomberg API
                </div>
                <div class="footer-section">
                    <span class="footer-info">Last updated: {current_date}</span><br>
                    <span class="footer-info">Version 1.1.0</span>
                </div>
                <div class="footer-section">
                    <span class="footer-info">Contact: Market Research & Economic Analysis</span><br>
                    <span class="footer-info">© 2025 Teck Resources Ltd.</span>
                </div>
            </div>
        </footer>

        <style type="text/css">
        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid #eaecef;
        }}
        .footer-content {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: #6c757d;
        }}
        .footer-section {{
            padding: 0 1rem;
        }}
        .footer-info {{
            font-size: 0.8rem;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the dashboard application."""
        start_time = datetime.now()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Dashboard application started")
        self.logger.info("Data logger initialized at path: %s", self.data_logger.log_dir)

        self.render_header()

        filters = self.render_filters()
        self.logger.info(f"Filters applied: {filters}")

        # Log the start of data loading
        self.logger.info(f"Loading data for {len(filters['selected_commodities'])} commodities")
        data = self.load_data(filters)
        self.logger.info(f"Data loaded successfully for {len(data)} commodities")

        # Capture a data snapshot for the current session
        self.data_logger.capture_data_snapshot(data, filters)

        # Log validation results for the loaded data
        validation_results = self.data_validator.validate_all_data(data)
        self.data_logger.log_validation_results(validation_results)

        # Create tabs for different views - cards first, then API status tab after detailed analysis
        cards_tab, overview_tab, details_tab, api_status_tab = st.tabs([
            "🔍 Price Cards",
            "📊 Market Overview",
            "📈 Detailed Analysis",
            "⚙️ API Status"
        ])

        with cards_tab:
            self.render_commodity_cards(data, filters)

        with overview_tab:
            self.render_overview_tab(data, filters)

        with details_tab:
            self.render_individual_tabs(data, filters)

        with api_status_tab:
            self.render_api_status_tab(data, filters)

        self.render_footer()

        # Log dashboard session metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        self.logger.info(f"Dashboard rendered in {duration:.2f} seconds")

        # Import the make_json_serializable function
        from utils.data_logger import make_json_serializable

        # Log usage statistics - ensure all data is JSON serializable
        usage_data = make_json_serializable({
            "timestamp": datetime.now().isoformat(),
            "filters_applied": filters,
            "commodities_loaded": list(data.keys()),
            "render_time_seconds": duration,
            "validation_summary": self.data_validator.get_validation_summary(validation_results)
        })

        # Save usage statistics to log file
        log_path = os.path.join(self.data_logger.log_dir, "dashboard_usage.json")

        try:
            # Load existing logs if file exists
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        existing_logs = json.load(f)
                except json.JSONDecodeError:
                    # Handle corrupt JSON files
                    self.logger.warning(f"Could not parse JSON in {log_path}, creating new file")
                    existing_logs = []
            else:
                existing_logs = []

            # Append new log entry
            existing_logs.append(usage_data)

            # Write updated logs
            with open(log_path, 'w') as f:
                # Import custom JSON encoder from data_logger
                from utils.data_logger import CustomJSONEncoder
                json.dump(existing_logs, f, indent=2, cls=CustomJSONEncoder)

            self.logger.info(f"Dashboard usage statistics logged to {log_path}")
        except Exception as e:
            self.logger.error(f"Failed to log dashboard usage: {e}")

        return data  # Return data for potential further analysis