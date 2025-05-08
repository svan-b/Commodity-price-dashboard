"""
Helper utilities for the commodity dashboard.
Contains functions for formatting, transformations, and UI helpers.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit as st
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TECK_BLUE, COPPER_ORANGE, CATEGORIES

def format_price(price, units):
    """
    Format price value based on units.
    
    Args:
        price (float): The price value
        units (str): Units of the price
        
    Returns:
        str: Formatted price string
    """
    if 'USD' in units:
        if 'MT' in units or 'ton' in units:
            return f"${price:,.2f}"  # Always use 2 decimal places
        elif 'troy oz' in units:
            return f"${price:,.2f}"
        elif 'kg' in units:
            return f"${price:,.2f}"
        elif 'lb' in units:
            return f"${price:,.3f}"  # 3 decimal places for smaller lb values
        elif 'barrel' in units:
            return f"${price:,.2f}"
        else:
            return f"${price:,.2f}"
    elif 'CNY' in units:
        return f"CNY {price:,.2f}"  # Using text instead of symbol to avoid encoding issues
    else:
        return f"{price:,.2f}"

def calculate_change(df):
    """
    Calculate price changes over various periods.
    
    Args:
        df (pd.DataFrame): DataFrame with Date and Price columns
        
    Returns:
        dict: Dictionary with price changes
    """
    if df.empty or len(df) < 2:
        return {
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
    
    # Sort by date to ensure correct calculation
    df = df.sort_values('Date')
    
    # Get the last price
    last_price = df['Price'].iloc[-1]
    previous_price = df['Price'].iloc[-2]
    
    # Get current date
    last_date = df['Date'].iloc[-1]
    
    # Calculate time deltas
    one_day_ago = last_date - timedelta(days=1)
    one_week_ago = last_date - timedelta(days=7)
    one_month_ago = last_date - timedelta(days=30)
    one_year_ago = last_date - timedelta(days=365)
    ytd_start = datetime(last_date.year, 1, 1)
    
    # Find closest prices for each time period
    def get_closest_price(target_date):
        closest_idx = (df['Date'] - target_date).abs().idxmin()
        return df['Price'].iloc[closest_idx]
    
    price_1d_ago = get_closest_price(one_day_ago)
    price_1w_ago = get_closest_price(one_week_ago)
    price_1m_ago = get_closest_price(one_month_ago)
    price_1y_ago = get_closest_price(one_year_ago)
    price_ytd = get_closest_price(ytd_start)
    
    # Calculate changes
    change_1d = last_price - price_1d_ago
    change_1d_pct = change_1d / price_1d_ago if price_1d_ago else 0
    
    change_1w = last_price - price_1w_ago
    change_1w_pct = change_1w / price_1w_ago if price_1w_ago else 0
    
    change_1m = last_price - price_1m_ago
    change_1m_pct = change_1m / price_1m_ago if price_1m_ago else 0
    
    change_1y = last_price - price_1y_ago
    change_1y_pct = change_1y / price_1y_ago if price_1y_ago else 0
    
    change_ytd = last_price - price_ytd
    change_ytd_pct = change_ytd / price_ytd if price_ytd else 0
    
    return {
        'last_price': last_price,
        'previous_price': previous_price,
        'change_1d': change_1d,
        'change_1d_pct': change_1d_pct,
        'change_1w': change_1w,
        'change_1w_pct': change_1w_pct,
        'change_1m': change_1m,
        'change_1m_pct': change_1m_pct,
        'change_1y': change_1y,
        'change_1y_pct': change_1y_pct,
        'change_ytd': change_ytd,
        'change_ytd_pct': change_ytd_pct
    }

def create_price_chart(df, commodity_name, units, color=TECK_BLUE):
    """
    Create a price chart for a commodity.
    
    Args:
        df (pd.DataFrame): DataFrame with Date and Price columns
        commodity_name (str): Name of the commodity
        units (str): Units of the price
        color (str): Line color for the chart
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Create figure
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Price'],
            mode='lines',
            name=commodity_name,
            line=dict(color=color, width=2)
        )
    )
    
    # Customize layout
    fig.update_layout(
        title=f"{commodity_name} Price History",
        xaxis_title="Date",
        yaxis_title=f"Price ({units})",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # Add range selector buttons
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def create_multi_commodity_chart(data_dict, category, units_filter=None):
    """
    Create a chart with multiple commodities.
    
    Args:
        data_dict (dict): Dictionary of commodity dataframes
        category (str): Category to filter by
        units_filter (str, optional): Filter by units
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    # Colors for different lines
    colors = [TECK_BLUE, COPPER_ORANGE, "#008080", "#800080", "#FF6347", "#4682B4", "#2E8B57"]
    color_idx = 0
    
    added_commodities = []
    
    for commodity_name, df in data_dict.items():
        if df.empty:
            continue
            
        # Check if we should include this commodity
        if 'Units' in df.columns and units_filter and df['Units'].iloc[0] != units_filter:
            continue
            
        # Sort by date
        df = df.sort_values('Date')
        
        # Normalize price to percentage change from first date
        first_price = df['Price'].iloc[0]
        df['Normalized'] = (df['Price'] / first_price - 1) * 100
        
        # Add trace
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['Normalized'],
                mode='lines',
                name=commodity_name,
                line=dict(color=colors[color_idx % len(colors)], width=2)
            )
        )
        
        added_commodities.append(commodity_name)
        color_idx += 1
    
    if not added_commodities:
        fig.add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Get category display name
    if category == 'all':
        category_display = "All Selected Commodities"
    else:
        category_display = CATEGORIES.get(category, category.capitalize())
    
    # Customize layout
    fig.update_layout(
        title=f"{category_display} - Price Change % (Normalized)",
        xaxis_title="Date",
        yaxis_title="% Change from First Date",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # Add range selector buttons
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    return fig

def get_data_update_text(df):
    """
    Get text about when data was last updated.
    
    Args:
        df (pd.DataFrame): DataFrame with Date column
        
    Returns:
        str: Text about data update
    """
    if df.empty:
        return "No data available"
        
    last_date = df['Date'].max()
    last_date_str = last_date.strftime("%B %d, %Y")
    
    current_date = datetime.now()
    days_ago = (current_date - last_date).days
    
    if days_ago == 0:
        days_text = "today"
    elif days_ago == 1:
        days_text = "yesterday"
    else:
        days_text = f"{days_ago} days ago"
        
    return f"Last updated: {last_date_str} ({days_text})"

def format_change_value(change, change_pct):
    """
    Format change values for display.
    
    Args:
        change (float): Absolute change
        change_pct (float): Percentage change
        
    Returns:
        tuple: (formatted text, color)
    """
    if change is None or change_pct is None:
        return "N/A", "gray"
        
    sign = "+" if change > 0 else ""
    text = f"{sign}{change:.2f} ({sign}{change_pct*100:.2f}%)"
    color = "green" if change > 0 else "red" if change < 0 else "gray"
    
    return text, color