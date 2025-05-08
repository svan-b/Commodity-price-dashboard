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

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TECK_BLUE, COPPER_ORANGE, BACKGROUND_WHITE, TEXT_COLOR,
    DASHBOARD_TITLE, DASHBOARD_SUBTITLE,
    DEFAULT_TIMEFRAME, DEFAULT_DATA_FREQUENCY, 
    AVAILABLE_TIMEFRAMES, AVAILABLE_FREQUENCIES,
    CATEGORIES, COMMODITIES
)
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
        self.configure_page()
        
    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=DASHBOARD_TITLE,
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply custom CSS for a more professional look
        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .main .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 1500px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {TECK_BLUE};
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 700;
        }}
        
        h2 {{
            font-size: 1.5rem;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        h3 {{
            font-size: 1.1rem;
            font-weight: 600;
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
            padding: 1.5rem;
            color: white;
            border-radius: 5px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .teck-logo {{
            font-weight: 700;
            font-size: 2rem;
            letter-spacing: -0.03em;
            margin-right: 1rem;
        }}
        
        .teck-header-content {{
            flex: 1;
        }}
        
        .price-card {{
            border: 1px solid #eaecef;
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            background-color: {BACKGROUND_WHITE};
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .price-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .price-card h3 {{
            margin-top: 0;
            color: {TECK_BLUE};
            font-size: 1.1rem;
            font-weight: 600;
            border-bottom: none;
            padding-bottom: 0;
        }}
        
        .price-value {{
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0.7rem 0;
            letter-spacing: -0.01em;
        }}
        
        .price-change {{
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 0.5rem;
        }}
        
        .price-change.positive {{
            color: #28a745;
            background-color: rgba(40, 167, 69, 0.1);
        }}
        
        .price-change.negative {{
            color: #dc3545;
            background-color: rgba(220, 53, 69, 0.1);
        }}
        
        .price-units {{
            color: #6c757d;
            font-size: 0.8rem;
            margin-bottom: 0.3rem;
        }}
        
        .data-source {{
            font-size: 0.7rem;
            color: #6c757d;
            margin-top: 0.5rem;
            border-top: 1px solid #f5f5f5;
            padding-top: 0.5rem;
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
                <p>{DASHBOARD_SUBTITLE}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_filters(self):
        """Render sidebar filters."""
        st.sidebar.title("Dashboard Controls")
        
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
            default=all_commodities[:10]  # Default to first 10 to avoid overwhelming the UI
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
    
    def load_data(self, filters):
        """
        Load commodity data based on filters.
        
        Args:
            filters (dict): Filter settings
            
        Returns:
            dict: Dictionary of commodity data
        """
        data = {}
        
        # Get commodity data for selected commodities
        for commodity_name in filters["selected_commodities"]:
            df = self.bloomberg_api.get_commodity_data(
                commodity_name,
                start_date=filters["start_date"],
                end_date=filters["end_date"],
                freq=filters["frequency"]
            )
            
            if not df.empty:
                data[commodity_name] = df
                
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
        for commodity_name, df in data.items():
            if df.empty:
                continue
                
            # Find category
            for commodity in COMMODITIES:
                if commodity['name'] == commodity_name:
                    category = commodity['category']
                    if category not in commodity_by_category:
                        commodity_by_category[category] = []
                    commodity_by_category[category].append((commodity_name, df))
                    break
        
        # Render cards by category
        for category, commodities in commodity_by_category.items():
            if not commodities:
                continue
                
            # Add category header
            st.markdown(f"## {CATEGORIES[category]}")
            
            # Create four-column layout for each category
            cols = st.columns(4)
            col_idx = 0
            
            for commodity_name, df in commodities:
                # Get metadata
                units = df["Units"].iloc[0] if "Units" in df.columns else "N/A"
                data_source = df["Data Source"].iloc[0] if "Data Source" in df.columns else "N/A"
                ticker = df["Ticker"].iloc[0] if "Ticker" in df.columns else "N/A"
                
                # Calculate changes
                changes = calculate_change(df)
                
                # Format last price
                last_price = changes['last_price']
                formatted_price = format_price(last_price, units) if last_price is not None else "N/A"
                
                # Format changes
                change_text, change_color = format_change_value(
                    changes['change_1d'], changes['change_1d_pct']
                )
                
                # Select column to render in
                col = cols[col_idx % 4]
                col_idx += 1
                
                with col:
                    # Render commodity card
                    col.markdown(f"""
                    <div class="price-card">
                        <h3>{commodity_name}</h3>
                        <div class="price-value">{formatted_price}</div>
                        <div class="price-change {change_color}">{change_text}</div>
                        <div class="price-units">{units}</div>
                        <div class="data-source">Source: {data_source} | {ticker}</div>
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
            
        tabs = st.tabs(list(data.keys()))
        
        for i, (commodity_name, df) in enumerate(data.items()):
            with tabs[i]:
                if df.empty:
                    st.warning(f"No data available for {commodity_name}.")
                    continue
                    
                # Get metadata
                units = df["Units"].iloc[0] if "Units" in df.columns else "N/A"
                data_source = df["Data Source"].iloc[0] if "Data Source" in df.columns else "N/A"
                ticker = df["Ticker"].iloc[0] if "Ticker" in df.columns else "N/A"
                commodity_type = df["Type"].iloc[0] if "Type" in df.columns else "N/A"
                
                # Create two columns
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Price chart
                    chart = create_price_chart(df, commodity_name, units)
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
                    
                    change_1d_text, change_1d_color = format_change_value(
                        changes['change_1d'], changes['change_1d_pct']
                    )
                    change_1w_text, change_1w_color = format_change_value(
                        changes['change_1w'], changes['change_1w_pct']
                    )
                    change_1m_text, change_1m_color = format_change_value(
                        changes['change_1m'], changes['change_1m_pct']
                    )
                    change_1y_text, change_1y_color = format_change_value(
                        changes['change_1y'], changes['change_1y_pct']
                    )
                    change_ytd_text, change_ytd_color = format_change_value(
                        changes['change_ytd'], changes['change_ytd_pct']
                    )
                    
                    st.markdown(f"""
                    | Period | Change |
                    | ------ | ------ |
                    | 1 Day | <span style="color:{change_1d_color}">{change_1d_text}</span> |
                    | 1 Week | <span style="color:{change_1w_color}">{change_1w_text}</span> |
                    | 1 Month | <span style="color:{change_1m_color}">{change_1m_text}</span> |
                    | 1 Year | <span style="color:{change_1y_color}">{change_1y_text}</span> |
                    | YTD | <span style="color:{change_ytd_color}">{change_ytd_text}</span> |
                    """, unsafe_allow_html=True)
                    
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
    
    def render_footer(self):
        """Render dashboard footer."""
        st.markdown("""
        <footer>
            Teck Resources Commodity Price Dashboard • Data retrieved via Bloomberg
            <br>
            Last updated: May 07, 2025
        </footer>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the dashboard application."""
        self.render_header()
        
        filters = self.render_filters()
        
        data = self.load_data(filters)
        
        # Create tabs for different views - put cards first
        cards_tab, overview_tab, details_tab = st.tabs([
            "🔍 Price Cards", 
            "📊 Market Overview", 
            "📈 Detailed Analysis"
        ])
        
        with cards_tab:
            self.render_commodity_cards(data, filters)
            
        with overview_tab:
            self.render_overview_tab(data, filters)
            
        with details_tab:
            self.render_individual_tabs(data, filters)
            
        self.render_footer()