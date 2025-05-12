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
    # Default format is 2 decimal places
    decimal_places = 2

    # Special case for lb which needs 3 decimal places
    if 'lb' in units:
        decimal_places = 3

    # Add currency symbol
    if 'USD' in units:
        return f"${price:,.{decimal_places}f}"
    elif 'CNY' in units:
        return f"CNY {price:,.{decimal_places}f}"  # Using text instead of symbol to avoid encoding issues
    else:
        return f"{price:,.{decimal_places}f}"

def get_sorted_dataframe(df):
    """
    Sort the dataframe by date and return a copy.
    
    Args:
        df (pd.DataFrame): DataFrame with Date column
        
    Returns:
        pd.DataFrame: Sorted DataFrame
    """
    if df.empty or len(df) < 2:
        return df
    return df.sort_values('Date').copy()

def get_date_frequency(df):
    """
    Determine the frequency of data by analyzing date differences.
    
    Args:
        df (pd.DataFrame): DataFrame with Date column
        
    Returns:
        tuple: (freq_type, avg_diff)
    """
    if df.empty or len(df) < 2:
        return "unknown", 30  # Default to monthly
    
    # Calculate the differences between consecutive dates
    date_diffs = []
    for i in range(1, min(len(df), 10)):  # Check up to 10 consecutive dates
        diff = (df['Date'].iloc[i] - df['Date'].iloc[i-1]).days
        date_diffs.append(diff)
    
    if not date_diffs:
        return "unknown", 30  # Default to monthly
    
    avg_diff = sum(date_diffs) / len(date_diffs)
    
    # Determine frequency type based on average difference
    if avg_diff < 3:
        return "daily", avg_diff
    elif avg_diff < 10:
        return "weekly", avg_diff
    else:
        return "monthly", avg_diff

def find_reference_price(df, last_date, freq_type):
    """
    Find the appropriate reference price based on frequency type.
    
    Args:
        df (pd.DataFrame): DataFrame with Date and Price columns
        last_date (datetime): The last date in the dataset
        freq_type (str): Frequency type (daily, weekly, or monthly)
        
    Returns:
        float: Previous price to use as reference
    """
    if df.empty or len(df) < 2:
        return df['Price'].iloc[0] if not df.empty else None
    
    previous_date_idx = None
    
    if freq_type == "daily":
        # For daily data, find a price 1-3 days before last date
        one_day_threshold = 3  # Maximum days to consider as "daily"
        
        for i in range(len(df) - 2, -1, -1):
            days_diff = (last_date - df['Date'].iloc[i]).days
            if days_diff >= 1 and days_diff <= one_day_threshold:
                previous_date_idx = i
                break
                
    elif freq_type == "weekly":
        # For weekly data, find price 5-10 days before last date
        for i in range(len(df) - 2, -1, -1):
            days_diff = (last_date - df['Date'].iloc[i]).days
            if days_diff >= 5 and days_diff <= 10:
                previous_date_idx = i
                break
                
        # If no point in that range, find nearest available point at least 3 days old
        if previous_date_idx is None:
            for i in range(len(df) - 2, -1, -1):
                if (last_date - df['Date'].iloc[i]).days >= 3:
                    previous_date_idx = i
                    break
                    
    else:  # monthly or unknown
        # For monthly data, find price 25-35 days before last date
        for i in range(len(df) - 2, -1, -1):
            days_diff = (last_date - df['Date'].iloc[i]).days
            if days_diff >= 25 and days_diff <= 35:
                previous_date_idx = i
                break
                
        # If no point in that range, find closest to 30 days ago but at least 7 days old
        if previous_date_idx is None:
            closest_diff = float('inf')
            for i in range(len(df) - 2, -1, -1):
                days_diff = abs((last_date - df['Date'].iloc[i]).days - 30)
                if days_diff < closest_diff and (last_date - df['Date'].iloc[i]).days > 7:
                    closest_diff = days_diff
                    previous_date_idx = i
                    
        # If still no suitable point, use any point at least 14 days old
        if previous_date_idx is None:
            for i in range(len(df) - 2, -1, -1):
                if (last_date - df['Date'].iloc[i]).days >= 14:
                    previous_date_idx = i
                    break
    
    # Default to second-to-last point if we couldn't find anything else
    if previous_date_idx is None and len(df) > 1:
        previous_date_idx = len(df) - 2
        
    return df['Price'].iloc[previous_date_idx] if previous_date_idx is not None else df['Price'].iloc[0]

def calc_price_change(current, previous):
    """
    Calculate absolute and percentage change with proper error handling.
    
    Args:
        current (float): Current price
        previous (float): Previous reference price
        
    Returns:
        tuple: (absolute_change, percentage_change)
    """
    if current is None or previous is None:
        return None, None
        
    abs_change = current - previous
    
    # Prevent division by zero or very small numbers
    if previous and abs(previous) > 0.0001:
        pct_change = abs_change / previous
    else:
        pct_change = 0
        
    return abs_change, pct_change

def find_period_price(df, last_date, period_days, label):
    """
    Find the most appropriate price point for a specific time period.
    
    Args:
        df (pd.DataFrame): DataFrame with Date and Price columns
        last_date (datetime): The last date in the dataset
        period_days (int): Target days back from last date
        label (str): Label for the period (e.g., '1d', '1w', '1m', '1y', 'ytd')
        
    Returns:
        tuple: (price, date, has_actual_data)
    """
    if df.empty:
        return None, None, False
        
    target_date = last_date - timedelta(days=period_days)
    
    # Filter data to only include dates on or before the target
    df_before = df[df['Date'] <= target_date]
    
    # No data before the target date
    if df_before.empty:
        # Get the earliest available data point
        earliest_price = df['Price'].iloc[0]
        earliest_date = df['Date'].iloc[0]
        return earliest_price, earliest_date, False
    
    # Handle different time periods
    if label == '1d':
        return find_daily_price(df, df_before, last_date)
    elif label == '1w':
        return find_weekly_price(df, df_before, last_date)
    elif label == '1m':
        return find_monthly_price(df, df_before, last_date)
    elif label == '1y':
        return find_yearly_price(df, df_before, last_date)
    elif label == 'ytd':
        return find_ytd_price(df, last_date)
    else:
        # Default fallback
        closest_price = df_before['Price'].iloc[-1]
        closest_date = df_before['Date'].iloc[-1]
        return closest_price, closest_date, False

def find_daily_price(df, df_before, last_date):
    """
    Find price point for daily change.
    
    Args:
        df (pd.DataFrame): Full DataFrame
        df_before (pd.DataFrame): Filtered DataFrame
        last_date (datetime): Last date in dataset
        
    Returns:
        tuple: (price, date, has_actual_data)
    """
    # For daily changes, try to find the exact previous trading day
    if len(df_before) >= 2:
        # Get the second-to-last data point in the filtered data
        closest_price = df_before['Price'].iloc[-1]
        closest_date = df_before['Date'].iloc[-1]
        days_diff = (last_date - closest_date).days
        # Use it if it's reasonably recent (within 5 days)
        is_actual = days_diff <= 5
    else:
        # Fall back to the earliest available data
        closest_price = df_before['Price'].iloc[-1]
        closest_date = df_before['Date'].iloc[-1]
        is_actual = False
        
    return closest_price, closest_date, is_actual

def find_weekly_price(df, df_before, last_date):
    """
    Find price point for weekly change.
    
    Args:
        df (pd.DataFrame): Full DataFrame
        df_before (pd.DataFrame): Filtered DataFrame
        last_date (datetime): Last date in dataset
        
    Returns:
        tuple: (price, date, has_actual_data)
    """
    # For weekly changes, look for data ~7 days ago
    # Try to find a data point 6-9 days ago first
    week_data = df_before[df_before['Date'] >= (last_date - timedelta(days=9))]
    week_data = week_data[week_data['Date'] <= (last_date - timedelta(days=6))]
    
    if not week_data.empty:
        # Use the data point closest to 7 days ago
        closest_idx = (week_data['Date'] - (last_date - timedelta(days=7))).abs().argmin()
        closest_price = week_data.iloc[closest_idx]['Price']
        closest_date = week_data.iloc[closest_idx]['Date']
        is_actual = True
    else:
        # Fall back to finding any point 5-14 days ago
        week_data = df_before[df_before['Date'] >= (last_date - timedelta(days=14))]
        if not week_data.empty:
            closest_idx = (week_data['Date'] - (last_date - timedelta(days=7))).abs().argmin()
            closest_price = week_data.iloc[closest_idx]['Price']
            closest_date = week_data.iloc[closest_idx]['Date']
            is_actual = True
        else:
            # Last resort: use the latest available data
            closest_price = df_before['Price'].iloc[-1]
            closest_date = df_before['Date'].iloc[-1]
            is_actual = False
            
    return closest_price, closest_date, is_actual

def find_monthly_price(df, df_before, last_date):
    """
    Find price point for monthly change.
    
    Args:
        df (pd.DataFrame): Full DataFrame
        df_before (pd.DataFrame): Filtered DataFrame
        last_date (datetime): Last date in dataset
        
    Returns:
        tuple: (price, date, has_actual_data)
    """
    # For monthly changes, look for data ~30 days ago
    # Try to find a data point 28-32 days ago first
    month_data = df_before[df_before['Date'] >= (last_date - timedelta(days=32))]
    month_data = month_data[month_data['Date'] <= (last_date - timedelta(days=28))]
    
    if not month_data.empty:
        # Use the data point closest to 30 days ago
        closest_idx = (month_data['Date'] - (last_date - timedelta(days=30))).abs().argmin()
        closest_price = month_data.iloc[closest_idx]['Price']
        closest_date = month_data.iloc[closest_idx]['Date']
        is_actual = True
    else:
        # Fall back to finding any point 20-40 days ago
        month_data = df_before[df_before['Date'] >= (last_date - timedelta(days=40))]
        if not month_data.empty:
            closest_idx = (month_data['Date'] - (last_date - timedelta(days=30))).abs().argmin()
            closest_price = month_data.iloc[closest_idx]['Price']
            closest_date = month_data.iloc[closest_idx]['Date']
            is_actual = True
        else:
            # Last resort: use the latest available data
            closest_price = df_before['Price'].iloc[-1]
            closest_date = df_before['Date'].iloc[-1]
            is_actual = False
            
    return closest_price, closest_date, is_actual

def find_yearly_price(df, df_before, last_date):
    """
    Find price point for yearly change.
    
    Args:
        df (pd.DataFrame): Full DataFrame
        df_before (pd.DataFrame): Filtered DataFrame
        last_date (datetime): Last date in dataset
        
    Returns:
        tuple: (price, date, has_actual_data)
    """
    # For yearly changes, look for data ~365 days ago
    # Try to find a data point 360-370 days ago first
    year_data = df_before[df_before['Date'] >= (last_date - timedelta(days=370))]
    year_data = year_data[year_data['Date'] <= (last_date - timedelta(days=360))]
    
    if not year_data.empty:
        # Use the data point closest to 365 days ago
        closest_idx = (year_data['Date'] - (last_date - timedelta(days=365))).abs().argmin()
        closest_price = year_data.iloc[closest_idx]['Price']
        closest_date = year_data.iloc[closest_idx]['Date']
        is_actual = True
    else:
        # Fall back to finding any point 300-430 days ago
        year_data = df_before[df_before['Date'] >= (last_date - timedelta(days=430))]
        if not year_data.empty:
            closest_idx = (year_data['Date'] - (last_date - timedelta(days=365))).abs().argmin()
            closest_price = year_data.iloc[closest_idx]['Price']
            closest_date = year_data.iloc[closest_idx]['Date']
            is_actual = True
        else:
            # Last resort: use the latest available data
            closest_price = df_before['Price'].iloc[-1]
            closest_date = df_before['Date'].iloc[-1]
            is_actual = False
            
    return closest_price, closest_date, is_actual

def find_ytd_price(df, last_date):
    """
    Find price point for year-to-date change.
    
    Args:
        df (pd.DataFrame): DataFrame with Date and Price columns
        last_date (datetime): Last date in dataset
        
    Returns:
        tuple: (price, date, has_actual_data)
    """
    # For YTD, we want data from Jan 1 of the current year
    jan_1 = datetime(last_date.year, 1, 1)
    jan_data = df[df['Date'] >= jan_1]
    
    if not jan_data.empty:
        # Use the earliest data point from this year
        closest_price = jan_data.iloc[0]['Price']
        closest_date = jan_data.iloc[0]['Date']
        is_actual = True
    else:
        # If no data from this year, use the latest data from last year
        last_year_data = df[df['Date'] <= jan_1]
        if not last_year_data.empty:
            closest_price = last_year_data.iloc[-1]['Price']
            closest_date = last_year_data.iloc[-1]['Date']
            is_actual = False
        else:
            # Fall back to the earliest available data
            closest_price = df['Price'].iloc[0]
            closest_date = df['Date'].iloc[0]
            is_actual = False
            
    return closest_price, closest_date, is_actual

def calculate_change(df):
    """
    Calculate price changes over various periods with intelligent handling of data frequency.

    Key improvements:
    1. Automatically detects data frequency (daily, weekly, monthly, etc.)
    2. Always calculates all periods for consistency across frequency selections
    3. Marks changes as "native" to the data's frequency
    4. Identifies the "best period" to display based on actual data frequency
    5. Maintains consistent results when switching frequency views

    Args:
        df (pd.DataFrame): DataFrame with Date and Price columns

    Returns:
        dict: Dictionary with price changes and metadata
    """
    # Handle empty dataframe case
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
    df = get_sorted_dataframe(df)

    # Get the last price and date
    last_price = df['Price'].iloc[-1]
    last_date = df['Date'].iloc[-1]

    # Determine data frequency
    freq_type, avg_diff = get_date_frequency(df)

    # Find appropriate reference price based on frequency
    previous_price = find_reference_price(df, last_date, freq_type)

    # Calculate recent change for the frequency-appropriate period
    change_recent, change_recent_pct = calc_price_change(last_price, previous_price)

    # Initialize results with basic change values
    result = {
        'last_price': last_price,
        'previous_price': previous_price,
        'freq_type': freq_type,
        'avg_days_between_points': avg_diff,
        'change_recent': change_recent,
        'change_recent_pct': change_recent_pct
    }

    # Get prices for each standard period
    price_1d, date_1d, has_1d_data = find_period_price(df, last_date, 1, '1d')
    price_1w, date_1w, has_1w_data = find_period_price(df, last_date, 7, '1w')
    price_1m, date_1m, has_1m_data = find_period_price(df, last_date, 30, '1m')
    price_1y, date_1y, has_1y_data = find_period_price(df, last_date, 365, '1y')

    # For YTD, calculate days since January 1st
    days_since_jan_1 = (last_date - datetime(last_date.year, 1, 1)).days
    price_ytd, date_ytd, has_ytd_data = find_period_price(df, last_date, days_since_jan_1, 'ytd')

    # ENHANCED APPROACH:
    # 1. Always calculate all changes for ALL periods
    # 2. Mark which ones are "native" to this data's frequency
    # 3. Identify "best" period for this data
    # 4. Provide metadata for UI to make intelligent decisions

    # Calculate which periods are "native" to this data frequency
    is_daily_native = freq_type == 'daily' and avg_diff <= 3
    is_weekly_native = (freq_type == 'weekly' and 3 < avg_diff <= 10) or (freq_type == 'daily' and not is_daily_native)
    is_monthly_native = (freq_type == 'monthly' and avg_diff > 10) or (not is_daily_native and not is_weekly_native)

    # Define the best display period based on actual data frequency
    if is_daily_native:
        best_period = '1d'
    elif is_weekly_native:
        best_period = '1w'
    else:  # monthly or other
        best_period = '1m'

    # Always calculate ALL changes for consistency regardless of frequency
    change_1d, change_1d_pct = calc_price_change(last_price, price_1d)
    change_1w, change_1w_pct = calc_price_change(last_price, price_1w)
    change_1m, change_1m_pct = calc_price_change(last_price, price_1m)
    change_1y, change_1y_pct = calc_price_change(last_price, price_1y)
    change_ytd, change_ytd_pct = calc_price_change(last_price, price_ytd)

    # Store all results with rich metadata about data quality
    result.update({
        # Changes
        'change_1d': change_1d,
        'change_1d_pct': change_1d_pct,
        'change_1w': change_1w,
        'change_1w_pct': change_1w_pct,
        'change_1m': change_1m,
        'change_1m_pct': change_1m_pct,
        'change_1y': change_1y,
        'change_1y_pct': change_1y_pct,
        'change_ytd': change_ytd,
        'change_ytd_pct': change_ytd_pct,

        # Reference dates
        'change_1d_date': date_1d,
        'change_1w_date': date_1w,
        'change_1m_date': date_1m,
        'change_1y_date': date_1y,
        'change_ytd_date': date_ytd,

        # Quality flags - which periods have actual data points (vs extrapolated)
        'change_1d_has_actual_data': has_1d_data,
        'change_1w_has_actual_data': has_1w_data,
        'change_1m_has_actual_data': has_1m_data,
        'change_1y_has_actual_data': has_1y_data,
        'change_ytd_has_actual_data': has_ytd_data,

        # Native frequency flags - which periods are native to this data frequency
        'change_1d_is_native': is_daily_native,
        'change_1w_is_native': is_weekly_native,
        'change_1m_is_native': is_monthly_native,
        'change_1y_is_native': True,  # Always consider yearly change native
        'change_ytd_is_native': True,  # Always consider YTD change native

        # For backwards compatibility with existing code
        'change_1d_is_duplicate': not has_1d_data,
        'change_1w_is_duplicate': not has_1w_data,
        'change_1m_is_duplicate': not has_1m_data,
        'change_1y_is_duplicate': not has_1y_data,
        'change_ytd_is_duplicate': not has_ytd_data,

        # Backward compatibility - which periods should be shown
        'change_1d_is_applicable': is_daily_native,
        'change_1w_is_applicable': is_weekly_native or is_daily_native,
        'change_1m_is_applicable': True,  # Always show monthly
        'change_1y_is_applicable': True,  # Always show yearly
        'change_ytd_is_applicable': True,  # Always show YTD

        # Best period for this data (for UI to make intelligent decisions)
        'best_period': best_period
    })

    return result

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
        title=dict(
            text=f"{commodity_name} Price History",
            font=dict(size=18, color="#00103f")
        ),
        xaxis_title=dict(text="Date", font=dict(size=14)),
        yaxis_title=dict(text=f"Price ({units})", font=dict(size=14)),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,  # Moved higher to avoid overlap with range selector
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        margin=dict(l=40, r=40, t=80, b=40),  # Increased margins for better spacing
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=450  # Set explicit height for better proportions
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
                dict(step="all", label="Max")
            ]),
            font=dict(size=12),
            bgcolor="#f8f9fa",
            bordercolor="#dddddd",
            borderwidth=1,
            y=0.99,  # Positioned below the legend
            x=0.01,  # Positioned at the left
            activecolor="#00103f"  # Teck blue for active button
        ),
        gridcolor='lightgray',
        tickfont=dict(size=12),  # Larger tick font size
        title_font=dict(size=14)  # Larger axis title font
    )

    # Set y-axis grid color and font sizes
    fig.update_yaxes(
        gridcolor='lightgray',
        tickfont=dict(size=12),  # Larger tick font size
        title_font=dict(size=14)  # Larger axis title font
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
    filtered_data = {}

    # Filter commodities based on criteria
    for commodity_name, df in data_dict.items():
        if df.empty:
            continue

        # Check if we should include this commodity based on units
        if 'Units' in df.columns and units_filter and df['Units'].iloc[0] != units_filter:
            continue

        # Sort by date and store filtered data
        df = df.sort_values('Date')
        filtered_data[commodity_name] = df.copy()

    # If no data left after filtering, return empty chart
    if not filtered_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig

    # Find common date range for proper normalization
    # For start date, find the latest start date among all commodities
    # This ensures we're comparing from a common starting point
    common_start_date = None
    for df in filtered_data.values():
        df_start_date = df['Date'].min()
        if common_start_date is None or df_start_date > common_start_date:
            common_start_date = df_start_date

    # Display info about normalization
    normalization_info = f"Data normalized from {common_start_date.strftime('%b %d, %Y')}"

    # Process and add each commodity with proper normalization
    for commodity_name, df in filtered_data.items():
        # Filter to common date range
        df_normalized = df[df['Date'] >= common_start_date].copy()

        if df_normalized.empty:
            continue

        # Get the base price for normalization (first price after common start date)
        base_price = df_normalized['Price'].iloc[0]

        # Calculate normalized values
        df_normalized['Normalized'] = (df_normalized['Price'] / base_price - 1) * 100

        # Add trace
        fig.add_trace(
            go.Scatter(
                x=df_normalized['Date'],
                y=df_normalized['Normalized'],
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
        title=dict(
            text=f"{category_display} - Price Change % (Normalized)",
            font=dict(size=18, color="#00103f")
        ),
        xaxis_title=dict(text="Date", font=dict(size=14)),
        yaxis_title=dict(text="% Change from Common Start Date", font=dict(size=14)),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,  # Moved higher to avoid overlap
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        margin=dict(l=40, r=40, t=80, b=40),  # Increased margins
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500  # Taller for comparison chart
    )

    # Add annotation about normalization date
    fig.add_annotation(
        text=normalization_info,
        xref="paper", yref="paper",
        x=0.5, y=-0.14,  # Position below x-axis
        showarrow=False,
        font=dict(size=10, color="#666666"),
        align="center"
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
                dict(step="all", label="Max")
            ]),
            font=dict(size=12),
            bgcolor="#f8f9fa",
            bordercolor="#dddddd",
            borderwidth=1,
            y=0.99,  # Positioned below the legend
            x=0.01,  # Positioned at the left
            activecolor="#00103f"  # Teck blue for active button
        ),
        gridcolor='lightgray',
        tickfont=dict(size=12),  # Larger tick font size
        title_font=dict(size=14)  # Larger axis title font
    )

    # Set y-axis grid color and font sizes
    fig.update_yaxes(
        gridcolor='lightgray',
        tickfont=dict(size=12),  # Larger tick font size
        title_font=dict(size=14)  # Larger axis title font
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

def format_change_value(change, change_pct, is_duplicate=False, is_applicable=True):
    """
    Format change values for display.

    Args:
        change (float): Absolute change
        change_pct (float): Percentage change
        is_duplicate (bool): Whether this change uses the same price as another period
        is_applicable (bool): Whether this change period is applicable for the data frequency

    Returns:
        tuple: (formatted text, color)
    """
    # If the period is not applicable for this data frequency, show N/A but use standard color
    # Use positive/negative colors to match the rest of the table
    if not is_applicable:
        return "N/A", "neutral"

    if change is None or change_pct is None:
        return "No data available", "neutral"

    # Ensure we have valid numbers
    try:
        change = float(change)
        change_pct = float(change_pct)
    except (ValueError, TypeError):
        return "Invalid data", "gray"

    # Handle edge cases
    if abs(change) < 0.000001 or abs(change_pct) < 0.000001:
        return "No change (0.00%)", "neutral"

    sign = "+" if change > 0 else ""

    # Format with appropriate precision based on magnitude and units
    if abs(change) < 0.1:
        change_str = f"{sign}{change:.4f}"
    elif abs(change) < 1:
        change_str = f"{sign}{change:.3f}"
    elif abs(change) < 10:
        change_str = f"{sign}{change:.2f}"
    elif abs(change) < 100:
        change_str = f"{sign}{change:.1f}"
    else:
        change_str = f"{sign}{change:.0f}"

    # Always show two decimal places for percentage
    pct_str = f"{sign}{change_pct*100:.2f}%"

    # Determine color class based on change direction
    if abs(change) < 0.000001 or abs(change_pct) < 0.000001:
        color_class = "neutral"
    elif change > 0:
        color_class = "positive"
    else:
        color_class = "negative"

    # Show different formatting for duplicate data points
    if is_duplicate:
        text = f"{change_str} ({pct_str}) *"  # Add an asterisk to indicate duplicate reference point
    else:
        text = f"{change_str} ({pct_str})"

    return text, color_class