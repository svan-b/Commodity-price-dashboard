"""
Configuration file for commodity dashboard.
Contains ticker mappings, categories, and UI settings.
"""

# Teck Resources Brand Colors
TECK_BLUE = "#00103f"
COPPER_ORANGE = "#b0350b"
BACKGROUND_WHITE = "#ffffff"
ACCENT_COLOR = "#b0350b"
TEXT_COLOR = "#000000"

# Commodity Categories - Organized by metal/commodity type
CATEGORIES = {
    "base_metals": "Base Metals",
    "precious_metals": "Precious Metals",
    "energy": "Energy",
    "rare_metals": "Rare Metals",
    "steel_materials": "Steel Materials"
}

# Commodity Configuration - Reorganized by logical metal groupings
COMMODITIES = [
    # BASE METALS - Top 3 first as specified
    {
        "name": "Copper (Cu)",
        "category": "base_metals",
        "preferred_ticker": "LMCADY Comdty",
        "description": "LME Copper Cash Settlement Price - Official daily price for copper determined by the London Metal Exchange",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot (LME Cash)",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#b87333"  # Copper color
    },
    {
        "name": "Zinc (Zn)",
        "category": "base_metals",
        "preferred_ticker": "LMZSDY Comdty",
        "description": "LME Zinc Cash Settlement Price - Official daily price for zinc determined by the London Metal Exchange",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot (LME Cash)",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#D3D4D5"  # Zinc color
    },
    {
        "name": "Nickel (Ni)",
        "category": "base_metals",
        "preferred_ticker": "LMNIDY Comdty",
        "description": "LME Nickel Cash Settlement Price - Official daily price for nickel determined by the London Metal Exchange",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot (LME Cash)",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#a3a9af"  # Nickel color
    },
    {
        "name": "Lead (Pb)",
        "category": "base_metals",
        "preferred_ticker": "LMPBDY Comdty",
        "description": "LME Lead Cash Settlement Price - Official daily price for lead determined by the London Metal Exchange",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot (LME Cash)",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#5C6274"  # Lead color
    },
    {
        "name": "Aluminum (Al)",
        "category": "base_metals",
        "preferred_ticker": "LMAHDY Comdty",
        "description": "LME Aluminum Cash Settlement Price - Official daily price for aluminum determined by the London Metal Exchange",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot (LME Cash)",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#848789"  # Aluminum color
    },
    
    # PRECIOUS METALS
    {
        "name": "Gold (Au)",
        "category": "precious_metals",
        "preferred_ticker": "XAU BGN Curncy",
        "description": "Gold Spot Price - Global benchmark price for gold in the interbank market",
        "alternative_ticker": "XAU",
        "alternative_description": "Simplified ticker for gold spot price",
        "type": "Spot",
        "units": "USD/troy oz",
        "data_source": "Bloomberg",
        "color": "#FFD700"  # Gold color
    },
    {
        "name": "Silver (Ag)",
        "category": "precious_metals",
        "preferred_ticker": "XAGUSD BGN Curncy",
        "description": "Silver Spot Price - Global benchmark price for silver in the interbank market",
        "alternative_ticker": "XAGUSD",
        "alternative_description": "Simplified ticker for silver spot price",
        "type": "Spot",
        "units": "USD/troy oz",
        "data_source": "Bloomberg",
        "color": "#C0C0C0"  # Silver color
    },
    {
        "name": "Platinum (Pt)",
        "category": "precious_metals",
        "preferred_ticker": "XPT BGN Curncy",
        "description": "Platinum Spot Price - Global benchmark price for platinum in the interbank market",
        "alternative_ticker": "XPT",
        "alternative_description": "Simplified ticker for platinum spot price",
        "type": "Spot",
        "units": "USD/troy oz",
        "data_source": "Bloomberg",
        "color": "#E5E4E2"  # Platinum color
    },
    
    # RARE METALS
    {
        "name": "Lithium (Li)",
        "category": "rare_metals",
        "preferred_ticker": "LJC1 Comdty",
        "description": "Lithium Carbonate CIF CJK (Fastmarkets) Futures - Cost, Insurance and Freight price for lithium carbonate delivered to China, Japan, and Korea",
        "alternative_ticker": "LFA1 Comdty",
        "alternative_description": "Lithium Hydroxide (LiOH) CIF CJK (Fastmarkets) Futures - Price for lithium hydroxide delivered to China, Japan, and Korea",
        "type": "Futures",
        "units": "USD/kg",
        "data_source": "Bloomberg",
        "color": "#B9C1C9"  # Lithium color
    },
    {
        "name": "Cobalt (Co)",
        "category": "rare_metals",
        "preferred_ticker": "LMCODY Comdty",
        "description": "LME Cobalt Cash Settlement Price - Official daily price for cobalt determined by the London Metal Exchange",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot (LME Cash)",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#5F9EA0"  # Cobalt color
    },
    {
        "name": "Germanium (Ge)",
        "category": "rare_metals",
        "preferred_ticker": "GECNMVKY AMTL Index",
        "description": "China Germanium Metal 99.99% FOB - Free on board price for high-purity germanium from China",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "USD/kg",
        "data_source": "Bloomberg",
        "color": "#7D7F7D"  # Germanium color
    },
    {
        "name": "Molybdenum (Mo)",
        "category": "rare_metals",
        "preferred_ticker": "MYB1 Comdty",
        "description": "LME Molybdenum (Platts) Generic Future - Exchange-traded futures contract for molybdenum based on Platts price assessments",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Futures",
        "units": "USD/lb",
        "data_source": "Bloomberg",
        "color": "#ADA8A8"  # Molybdenum color
    },
    {
        "name": "Uranium (U)",
        "category": "rare_metals",
        "preferred_ticker": "UXCPSPTW UXCF Index",
        "description": "Weekly UxC Uranium U308 Weekly Spot Price - Industry standard weekly spot price assessment for uranium oxide",
        "alternative_ticker": "UXA1 Comdty",
        "alternative_description": "NYMEX UxC Uranium U308 Swap Futures - Exchange-traded uranium futures contract",
        "type": "Weekly Spot / Futures",
        "units": "USD/lb",
        "data_source": "Bloomberg",
        "color": "#AFE313"  # Uranium color (yellowcake)
    },
    {
        "name": "Antimony (Sb)",
        "category": "rare_metals",
        "preferred_ticker": "CCSMANT1 Index",
        "description": "China Shanghai Changjiang Antimony Grade 1 Spot Price - Benchmark price for antimony in China's domestic market",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "CNY/MT",
        "data_source": "Bloomberg",
        "color": "#383428"  # Antimony color
    },
    {
        "name": "Indium (In)",
        "category": "rare_metals",
        "preferred_ticker": "IUCNRZYP SMET Index",
        "description": "China Indium 99.99% Shanghai Spot - Benchmark price for high-purity indium in China",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "CNY/kg",
        "data_source": "Bloomberg",
        "color": "#A9A9A9"  # Indium color
    },
    {
        "name": "Cadmium (Cd)",
        "category": "rare_metals",
        "preferred_ticker": "CMCNCUJV AMTL Index",
        "description": "China Cadmium Ingot 99.99% EXW - Ex-works price for high-purity cadmium from Chinese producers",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "CNY/MT",
        "data_source": "Bloomberg",
        "color": "#7B7B7B"  # Cadmium color
    },
    
    # ENERGY
    {
        "name": "Oil (WTI)",
        "category": "energy",
        "preferred_ticker": "USCRWTIC Index",
        "description": "Crude Oil Domestic Sweet (DSW) Cushing Cash Formula - WTI crude oil price at Cushing, Oklahoma delivery point",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "USD/barrel",
        "data_source": "Bloomberg",
        "color": "#000000"  # Oil color
    },
    {
        "name": "WCS Differential",
        "category": "energy",
        "preferred_ticker": "WC1DSPOT MRXI Index",
        "description": "Western Canada Select Crude Oil at Cushing OK Physical vs WTI Differential Spot - Price spread between WCS and WTI crudes",
        "alternative_ticker": "USCRWCAS Index",
        "alternative_description": "Crude Oil Western Canada Select (WCS) - Direct price for Western Canadian Select crude oil",
        "type": "Spot Differential / Spot Price",
        "units": "USD/barrel",
        "data_source": "Bloomberg",
        "color": "#4A0404"  # WCS color (darker than WTI)
    },
    {
        "name": "Natural Gas (AECO)",
        "category": "energy",
        "preferred_ticker": "NGCDAECO BNGC Index",
        "description": "AECO Natural Gas Spot Price - Benchmark for Canadian natural gas prices",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "CAD/GJ",
        "data_source": "Bloomberg",
        "color": "#6F8FAF"  # Natural gas color
    },
    {
        "name": "Sulphur",
        "category": "energy",
        "preferred_ticker": None,
        "description": "Sulphur price data - not available on Bloomberg",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Spot",
        "units": "USD/MT",
        "data_source": "Sample Data (Not Available on Bloomberg)",
        "color": "#FFFF00"  # Sulphur color
    },
    
    # STEEL MATERIALS
    {
        "name": "Iron Ore",
        "category": "steel_materials",
        "preferred_ticker": "ISIX62IU Index",
        "description": "Iron Ore Spot Price Index 62% Import Fine Ore CFR Qingdao - Benchmark price for iron ore delivered to Qingdao port in China",
        "alternative_ticker": "CN62SPOT KLSH Index",
        "alternative_description": "China Iron Ore 62% Fe Swap Spot - Alternative benchmark for iron ore imports to China",
        "type": "Spot",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#A52A2A"  # Iron color
    },
    {
        "name": "Iron Ore Futures",
        "category": "steel_materials",
        "preferred_ticker": "SCOM5 COMB Comdty",
        "description": "SGX Iron Ore 62% TSI Iron Ore Active Futures - Singapore Exchange futures contract for iron ore",
        "alternative_ticker": None,
        "alternative_description": None,
        "type": "Futures",
        "units": "USD/MT",
        "data_source": "Bloomberg",
        "color": "#8B4513"  # Iron futures color
    },
    {
        "name": "US HRC Steel",
        "category": "steel_materials",
        "preferred_ticker": "HRC1 Comdty",
        "description": "US Midwest Domestic Hot-Rolled Coil Steel Index Futures - CME futures contract for US hot-rolled coil steel",
        "alternative_ticker": "STANHCXW KLSH Index",
        "alternative_description": "North America Steel Hot Rolled Coil (HRC) Spot Ex-Works - Spot price for HRC at the mill",
        "type": "Futures / Spot",
        "units": "USD/short ton",
        "data_source": "Bloomberg",
        "color": "#708090"  # Steel color
    }
}
]

# Dashboard settings
DASHBOARD_TITLE = "Commodity Price Dashboard"
DASHBOARD_SUBTITLE = "Market Research and Economic Analysis"
DEFAULT_TIMEFRAME = "1Y"  # Options: 1M, 3M, 6M, 1Y, 5Y
DEFAULT_DATA_FREQUENCY = "monthly"  # Options: daily, weekly, monthly
AVAILABLE_TIMEFRAMES = ["1M", "3M", "6M", "1Y", "5Y"]
AVAILABLE_FREQUENCIES = ["daily", "weekly", "monthly"]

# Date settings
import datetime

# Generate sample data for commodities without Bloomberg data
def generate_sample_data():
    """Generate sample price data for commodities without Bloomberg access."""
    import pandas as pd
    import numpy as np
    
    today = datetime.datetime.now()
    
    # Generate 5 years of monthly data
    dates = pd.date_range(end=today, periods=60, freq='M')
    
    # Generate sample data for all commodities to use as fallback
    sample_data = {}
    
    # Sample data with realistic price ranges for each commodity
    for commodity in COMMODITIES:
        commodity_name = commodity['name']
        
        # Set appropriate price range based on commodity type
        if 'units' in commodity:
            if 'USD/MT' in commodity['units']:
                base = 2000
                volatility = 300
            elif 'USD/lb' in commodity['units']:
                base = 3
                volatility = 0.5
            elif 'USD/troy oz' in commodity['units']:
                if 'Gold' in commodity_name:
                    base = 1800
                    volatility = 200
                elif 'Silver' in commodity_name:
                    base = 25
                    volatility = 3
                elif 'Platinum' in commodity_name:
                    base = 1000
                    volatility = 100
                else:
                    base = 100
                    volatility = 20
            elif 'USD/kg' in commodity['units']:
                base = 20
                volatility = 5
            elif 'USD/barrel' in commodity['units']:
                base = 80
                volatility = 15
            elif 'CNY' in commodity['units']:
                base = 15000
                volatility = 2000
            else:
                base = 100
                volatility = 20
        else:
            base = 100
            volatility = 20
        
        # Create a time series with trend and seasonality
        t = np.linspace(0, 1, len(dates))
        trend = base + volatility * (np.sin(t * 6) + 0.2 * np.cos(t * 15)) 
        seasonality = volatility * 0.2 * np.sin(np.linspace(0, 12 * 5, len(dates)))
        noise = np.random.normal(0, volatility * 0.1, size=len(dates))
        
        # Combine components
        prices = trend + seasonality + noise
        
        # Ensure no negative prices
        prices = np.maximum(prices, base * 0.5)
        
        # Create dataframe
        sample_data[commodity_name] = pd.DataFrame({
            'Date': dates,
            'Price': prices
        })
    
    return sample_data