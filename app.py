import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as px_go
from plotly.subplots import make_subplots

# Page Configuration
st.set_page_config(
    page_title="Amazon Search Query Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #ff9900;
        margin-bottom: 15px;
    }
    .insight-card {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #1e88e5;
        margin-bottom: 15px;
    }
    .leakage-card {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #e53935;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: bold;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Expecting the file in the same directory
    df = pd.read_csv('US_Search_Query_Performance_Brand_View_Comprehensive_Month_2026_06_30.csv', skiprows=1)
    
    # Clean percentages and monetary fields
    numeric_cols = [
        'Search Query Volume', 'Impressions: Total Count', 'Impressions: Brand Count', 'Impressions: Brand Share %',
        'Clicks: Total Count', 'Clicks: Click Rate %', 'Clicks: Brand Count', 'Clicks: Brand Share %',
        'Clicks: Price (Median)', 'Clicks: Brand Price (Median)', 'Cart Adds: Total Count', 'Cart Adds: Brand Count',
        'Cart Adds: Brand Share %', 'Purchases: Total Count', 'Purchases: Purchase Rate %', 'Purchases: Brand Count',
        'Purchases: Brand Share %', 'Purchases: Price (Median)', 'Purchases: Brand Price (Median)'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Advanced metrics calculation
    df['Click_to_Cart_Rate_Brand'] = np.where(df['Clicks: Brand Count'] > 0, (df['Cart Adds: Brand Count'] / df['Clicks: Brand Count']) * 100, 0)
    df['Cart_to_Purchase_Rate_Brand'] = np.where(df['Cart Adds: Brand Count'] > 0, (df['Purchases: Brand Count'] / df['Cart Adds: Brand Count']) * 100, 0)
    df['Price_Premium_vs_Market'] = df['Clicks: Brand Price (Median)'] - df['Clicks: Price (Median)']
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Please ensure 'US_Search_Query_Performance_Brand_View_Comprehensive_Month_2026_06_30.csv' is available. Error: {e}")
    st.stop()

# Sidebar Layout
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=150)
st.sidebar.title("🎛️ Global Controls")
st.sidebar.markdown("---")

# Filters
min_volume = st.sidebar.slider("Minimum Search Volume", int(df['Search Query Volume'].min()), int(df['Search Query Volume'].max()), 500)
search_filter = st.sidebar.text_input("🔍 Search Keyword", "").lower()

# Filter dataset
filtered_df = df[df['Search Query Volume'] >= min_volume]
if search_filter:
    filtered_df = filtered_df[filtered_df['Search Query'].str.lower().str.contains(search_filter)]

# Header
st.title("📊 Amazon Search Query Performance Interactive Dashboard")
st.markdown("### **Brand:** Life Line | **Reporting Period:** June 2026")
st.markdown("---")

# Tabs Layout
tab_macro, tab_opps, tab_leakage, tab_shipping = st.tabs([
    "📈 Macro Funnel Breakdown", 
    "🎯 PPC Target Discovery", 
    "🚨 Budget Leakage Analytics", 
    "🚚 Shipping Speed Metrics"
])

# ---------------------------------------------------------------------------------
# TAB 1: Macro Funnel Breakdown
# ---------------------------------------------------------------------------------
with tab_macro:
    st.subheader("📌 Executive Scorecard & Funnel Performance")
    
    col1, col2, col3 = st.columns(3)
    
    # Calculations
    total_impressions = filtered_df['Impressions: Total Count'].sum()
    brand_impressions = filtered_df['Impressions: Brand Count'].sum()
    imp_share = (brand_impressions / total_impressions * 100) if total_impressions > 0 else 0
    
    total_clicks = filtered_df['Clicks: Total Count'].sum()
    brand_clicks = filtered_df['Clicks: Brand Count'].sum()
    clk_share = (brand_clicks / total_clicks * 100) if total_clicks > 0 else 0
    
    total_purchases = filtered_df['Purchases: Total Count'].sum()
    brand_purchases = filtered_df['Purchases: Brand Count'].sum()
    pur_share = (brand_purchases / total_purchases * 100) if total_purchases > 0 else 0
    
    with col1:
        st.markdown(f"""<div class='metric-card'>
            <h4>👀 Impressions Breakdown</h4>
            <h2>{brand_impressions:,}</h2>
            <p>Brand Impression Share: <b>{imp_share:.2f}%</b></p>
            <small>Market Total: {total_impressions:,}</small>
        </div>""", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #2196f3;'>
            <h4>🖱️ Click Conversion Pipeline</h4>
            <h2>{brand_clicks:,}</h2>
            <p>Brand Click Share: <b>{clk_share:.2f}%</b></p>
            <small>Market Total: {total_clicks:,}</small>
        </div>""", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #4caf50;'>
            <h4>💰 Absolute Purchase Layer</h4>
            <h2>{brand_purchases:,}</h2>
            <p>Brand Purchase Share: <b>{pur_share:.2f}%</b></p>
            <small>Market Total: {total_purchases:,}</small>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Macro Funnel Progression vs Category")
    
    # Funnel visualization using plotly
    fig_funnel = px_go.Figure()
    fig_funnel.add_trace(px_go.Funnel(
        name = 'Market Total Pipeline',
        y = ['Impressions', 'Clicks', 'Purchases'],
        x = [total_impressions, total_clicks, total_purchases],
        textinfo = "value+percent initial",
        marker = {"color": "#b0bec5"}
    ))
    fig_funnel.add_trace(px_go.Funnel(
        name = 'Brand Share Flow',
        y = ['Impressions', 'Clicks', 'Purchases'],
        x = [brand_impressions, brand_clicks, brand_purchases],
        textinfo = "value+percent initial",
        marker = {"color": "#ff9900"}
    ))
    fig_funnel.update_layout(title="Full Funnel Attrition: Brand vs Total Market")
    st.plotly_chart(fig_funnel, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 2: PPC Target Discovery
# ---------------------------------------------------------------------------------
with tab_opps:
    st.subheader("🎯 Scalable Brand Acquisition & Defense Opportunities")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div class='insight-card'><b>🔥 Market Share Conquesting Opportunities</b><br>High-volume keywords where your brand purchase share is low or zero. Target these immediately in Exact Match campaigns.</div>", unsafe_allow_html=True)
        conquest_df = filtered_df[filtered_df['Purchases: Brand Share %'] < 5].sort_values(by='Search Query Volume', ascending=False).head(10)
        st.dataframe(conquest_df[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Purchases: Brand Share %']], use_container_width=True)
        
    with col_right:
        st.markdown("<div class='insight-card' style='background-color: #e8f5e9; border-left-color: #4caf50;'><b>🛡️ Brand Stronghold Defenses</b><br>Keywords where you own the majority of conversions. Protect these with high defensive ad placements.</div>", unsafe_allow_html=True)
        defense_df = filtered_df[filtered_df['Purchases: Brand Share %'] >= 40].sort_values(by='Search Query Volume', ascending=False).head(10)
        st.dataframe(defense_df[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Purchases: Brand Share %']], use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Price Sensitivity Analysis vs Market Median")
    fig_price = px.scatter(
        filtered_df[filtered_df['Clicks: Brand Count'] > 0],
        x="Price_Premium_vs_Market",
        y="Purchases: Brand Share %",
        size="Search Query Volume",
        hover_name="Search Query",
        color="Clicks: Brand Price (Median)",
        title="Impact of Brand Price Premium on Purchase Share (Bubble Size = Search Volume)",
        labels={"Price_Premium_vs_Market": "Price Premium vs Market Median ($)", "Purchases: Brand Share %": "Brand Purchase Share %"}
    )
    st.plotly_chart(fig_price, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 3: Budget Leakage Analytics
# ---------------------------------------------------------------------------------
with tab_leakage:
    st.subheader("🚨 Ad Spend Leakage & Micro-Conversion Drop-off")
    st.markdown("<div class='leakage-card'><b>High Wasted Spend Warning:</b> The keywords below are generating notable brand click traffic, but result in <b>zero purchases</b>. Consider adding them as Phrase/Exact Negatives or reviewing landing page relevance.</div>", unsafe_allow_html=True)
    
    leakage_data = filtered_df[(filtered_df['Clicks: Brand Count'] >= 3) & (filtered_df['Purchases: Brand Count'] == 0)].sort_values(by='Clicks: Brand Count', ascending=False)
    
    if not leakage_data.empty:
        st.dataframe(leakage_data[['Search Query', 'Search Query Volume', 'Clicks: Brand Count', 'Cart Adds: Brand Count', 'Clicks: Brand Price (Median)']], use_container_width=True)
    else:
        st.success("🎉 No high leakage terms found matching current thresholds.")
        
    st.markdown("---")
    st.subheader("⚠️ Abandoned Cart Analysis")
    st.markdown("Keywords where customers added your products to the cart but failed to check out. (High Intent, Low Conversion)")
    
    filtered_df['Cart_Abandonment_Rate'] = 100 - filtered_df['Cart_to_Purchase_Rate_Brand']
    abandon_df = filtered_df[(filtered_df['Cart Adds: Brand Count'] > 2) & (filtered_df['Purchases: Brand Count'] < filtered_df['Cart Adds: Brand Count'])].sort_values(by='Cart Adds: Brand Count', ascending=False).head(10)
    
    fig_abandon = px.bar(
        abandon_df,
        x='Search Query',
        y='Cart Adds: Brand Count',
        color='Purchases: Brand Count',
        title="Top Abandoned Cart Opportunities (Color Indicates Completed Purchases)",
        labels={'Cart Adds: Brand Count': 'Brand Cart AddsCount'}
    )
    st.plotly_chart(fig_abandon, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 4: Shipping Speed Metrics
# ---------------------------------------------------------------------------------
with tab_shipping:
    st.subheader("🚚 Shipping Speed Distribution & Purchase Velocity")
    st.markdown("Analyze how logistics options (Same Day, 1-Day, 2-Day Shipping) affect click distribution across the platform.")
    
    shipping_labels = ['Same Day Shipping', '1-Day Shipping', '2-Day Shipping']
    shipping_counts = [
        filtered_df['Clicks: Same Day Shipping Speed'].sum(),
        filtered_df['Clicks: 1D Shipping Speed'].sum(),
        filtered_df['Clicks: 2D Shipping Speed'].sum()
    ]
    
    fig_ship = px.pie(
        names=shipping_labels,
        values=shipping_counts,
        title="Funnel Purchase / Click Logistics Breakdown",
        color_discrete_sequence=px.colors.sequential.Oranges_r
    )
    st.plotly_chart(fig_ship, use_container_width=True)

st.markdown("---")
st.info("💡 Data source fully derived from Amazon Search Query Performance Report (Brand View) - June 2026.")
