"""
Simplified Streamlit app for testing deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

def main():
    st.set_page_config(
        page_title="Commodity Dashboard Test",
        page_icon="📊",
        layout="wide"
    )

    st.title("Commodity Dashboard - Deployment Test")

    st.markdown("""
    This is a simplified test app to verify that Streamlit Cloud deployment is working.
    """)

    # Show environment information
    st.header("Environment Information")

    # Create three columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Python Info")
        st.code(f"Python version: {sys.version}")
        st.code(f"Current working directory: {os.getcwd()}")

    with col2:
        st.subheader("Package Versions")
        st.code(f"Streamlit: {st.__version__}")
        st.code(f"Pandas: {pd.__version__}")
        st.code(f"NumPy: {np.__version__}")

    # Directory structure
    st.header("Directory Structure")
    try:
        files_in_cwd = os.listdir('.')
        st.json({"current_dir_files": files_in_cwd})

        # Try to list parent directory
        parent_files = os.listdir('..')
        st.json({"parent_dir_files": parent_files})

        # Show src directory contents if available
        if os.path.exists('src'):
            src_files = os.listdir('src')
            st.json({"src_dir_files": src_files})

        # Show streamlit_deploy directory contents
        if os.path.exists('streamlit_deploy'):
            deploy_files = os.listdir('streamlit_deploy')
            st.json({"streamlit_deploy_files": deploy_files})
    except Exception as e:
        st.error(f"Error listing directory: {str(e)}")

    # Create a simple dataframe and chart to test plotting capabilities
    st.header("Sample Chart")

    data = pd.DataFrame({
        'Commodity': ['Copper', 'Gold', 'Silver', 'Platinum', 'Oil'],
        'Price': [9000, 1800, 22, 900, 75],
        'Change': [2.5, -0.8, 1.2, -0.5, 3.1]
    })

    st.dataframe(data)

    st.bar_chart(data.set_index('Commodity')['Price'])

    # Test interactive elements
    st.header("Interactive Elements")

    selected_commodity = st.selectbox(
        "Select a commodity to view",
        options=data['Commodity'].tolist()
    )

    st.write(f"You selected: {selected_commodity}")

    selected_row = data[data['Commodity'] == selected_commodity]

    st.metric(
        label=f"{selected_commodity} Price",
        value=f"${selected_row['Price'].values[0]:,.2f}",
        delta=f"{selected_row['Change'].values[0]:+.2f}%"
    )

    # Add a note about deployment status
    st.sidebar.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 0.9rem;">
        <p style="margin: 0; font-weight: bold;">Streamlit Cloud Deployment</p>
        <p style="margin: 5px 0 0 0;">Running in simplified mode</p>
        <p style="margin: 5px 0 0 0; font-size: 0.8rem;">This simplified app is used to verify that basic functionality is working.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()