"""
Fully standalone Streamlit app for cloud deployment.
This file has no external dependencies other than standard libraries and Streamlit.
"""

import os
import sys
import logging
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Main function that runs the Streamlit app."""
    st.set_page_config(
        page_title="Commodity Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Commodity Price Dashboard")
    
    st.markdown("""
    ## Welcome to the Commodity Price Dashboard
    
    This dashboard shows price information for various commodities.
    """)
    
    # Display environment information in sidebar
    st.sidebar.title("Environment Info")
    st.sidebar.code(f"Python version: {sys.version}")
    st.sidebar.code(f"Working directory: {os.getcwd()}")
    
    st.sidebar.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 0.9rem;">
        <p style="margin: 0; font-weight: bold;">Streamlit Cloud Deployment</p>
        <p style="margin: 5px 0 0 0;">Running in standalone mode</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Function to generate sample data
    def generate_sample_data():
        commodities = [
            {"name": "Copper", "units": "USD/MT", "base_price": 9000, "volatility": 500},
            {"name": "Gold", "units": "USD/troy oz", "base_price": 1800, "volatility": 200},
            {"name": "Silver", "units": "USD/troy oz", "base_price": 25, "volatility": 3},
            {"name": "Oil", "units": "USD/barrel", "base_price": 80, "volatility": 10},
            {"name": "Natural Gas", "units": "USD/MMBtu", "base_price": 3.5, "volatility": 0.5}
        ]
        
        # Generate dates for the past year
        today = datetime.now()
        dates = pd.date_range(end=today, periods=365, freq='D')
        
        all_data = {}
        
        for commodity in commodities:
            # Time factor for trend
            t = np.linspace(0, 1, len(dates))
            
            # Generate prices with trend, seasonality and noise
            base = commodity["base_price"]
            vol = commodity["volatility"]
            
            trend = base + vol * 0.3 * np.sin(t * 4)
            seasonality = vol * 0.1 * np.sin(np.linspace(0, 6, len(dates)))
            noise = np.random.normal(0, vol * 0.05, size=len(dates))
            
            prices = trend + seasonality + noise
            prices = pd.Series(prices).rolling(window=5, min_periods=1).mean().values
            
            # Create the dataframe
            df = pd.DataFrame({
                "Date": dates,
                "Price": prices,
                "Commodity": commodity["name"],
                "Units": commodity["units"]
            })
            
            all_data[commodity["name"]] = df
        
        return all_data
    
    # Generate sample data
    data = generate_sample_data()
    
    # Get the list of commodities
    commodities = list(data.keys())
    
    # Create tabs
    tab1, tab2 = st.tabs(["Price Overview", "Detailed Analysis"])
    
    with tab1:
        # Show price cards for each commodity
        st.subheader("Current Prices")
        
        # Create rows with 3 columns each
        columns = st.columns(3)
        
        for i, commodity_name in enumerate(commodities):
            df = data[commodity_name]
            col = columns[i % 3]
            
            with col:
                latest_price = df["Price"].iloc[-1]
                prev_price = df["Price"].iloc[-30]  # ~1 month ago
                change = latest_price - prev_price
                pct_change = (change / prev_price) * 100
                
                units = df["Units"].iloc[0]
                
                # Format the price
                if "USD" in units:
                    formatted_price = f"${latest_price:,.2f}"
                else:
                    formatted_price = f"{latest_price:,.2f}"
                
                # Create the price card with styled container
                st.markdown(f"""
                <div style="border: 1px solid #eaecef; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h3 style="margin-top: 0; color: #00103f;">{commodity_name}</h3>
                    <div style="font-size: 24px; font-weight: 700; margin: 10px 0;">{formatted_price}</div>
                    <div style="color: {'#28a745' if pct_change > 0 else '#dc3545'}; font-weight: 700;">
                        {pct_change:+.2f}%
                    </div>
                    <div style="color: #6c757d; font-size: 14px; margin-top: 5px;">{units}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        # Create a commodity selector
        selected_commodity = st.selectbox("Select Commodity", options=commodities)
        
        # Get the data for the selected commodity
        df = data[selected_commodity]
        
        # Create a chart
        st.subheader(f"{selected_commodity} Price History")
        
        chart_data = df[["Date", "Price"]].copy()
        st.line_chart(chart_data.set_index("Date"))
        
        # Add statistics
        st.subheader("Price Statistics")
        
        # Calculate statistics
        avg_price = df["Price"].mean()
        max_price = df["Price"].max()
        min_price = df["Price"].min()
        max_date = df.loc[df["Price"].idxmax(), "Date"]
        min_date = df.loc[df["Price"].idxmin(), "Date"]
        
        units = df["Units"].iloc[0]
        
        # Format price values
        if "USD" in units:
            avg_price_fmt = f"${avg_price:.2f}"
            max_price_fmt = f"${max_price:.2f}"
            min_price_fmt = f"${min_price:.2f}"
        else:
            avg_price_fmt = f"{avg_price:.2f}"
            max_price_fmt = f"{max_price:.2f}"
            min_price_fmt = f"{min_price:.2f}"
        
        # Display statistics
        cols = st.columns(3)
        cols[0].metric("Average Price", avg_price_fmt)
        cols[1].metric("Maximum Price", max_price_fmt, f"on {max_date.strftime('%Y-%m-%d')}")
        cols[2].metric("Minimum Price", min_price_fmt, f"on {min_date.strftime('%Y-%m-%d')}")
        
        # Show price table
        st.subheader("Recent Price Data")
        
        # Display the last 10 days of data
        recent_data = df.sort_values("Date", ascending=False).head(10)
        recent_data["Date"] = recent_data["Date"].dt.strftime("%Y-%m-%d")
        
        if "USD" in units:
            recent_data["Formatted Price"] = recent_data["Price"].apply(lambda x: f"${x:.2f}")
        else:
            recent_data["Formatted Price"] = recent_data["Price"].apply(lambda x: f"{x:.2f}")
            
        st.dataframe(recent_data[["Date", "Formatted Price"]], hide_index=True)
    
    # Footer
    st.markdown("""
    <footer style="margin-top: 50px; text-align: center; color: #6c757d; font-size: 12px; border-top: 1px solid #eaecef; padding-top: 10px;">
        Commodity Price Dashboard | Sample Data | Running on Streamlit Cloud
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()