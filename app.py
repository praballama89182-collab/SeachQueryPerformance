import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------------
# PAGE OPTIONS & STYLING (Corporate Deep Blue Theme)
# ---------------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon SQP Master Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color Grading Palette from user specification
HEX_BG = "#FBFBFC"
HEX_LIGHT_BLUE = "#D5DEE7"
HEX_DARK_SLATE = "#3A414B"
HEX_DEEP_BLUE = "#1652A3"
HEX_VIBRANT_BLUE = "#2F88F5"

st.markdown(f"""
    <style>
    .main {{ background-color: {HEX_BG}; }}
    .metric-card {{
        background-color: #ffffff;
        padding: 22px;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        border-top: 4px solid {HEX_DEEP_BLUE};
        margin-bottom: 15px;
        color: {HEX_DARK_SLATE};
    }}
    .metric-card h4 {{ margin: 0 0 8px 0; color: #7f8c8d; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .metric-card h2 {{ margin: 0; color: {HEX_DEEP_BLUE}; font-size: 32px; font-weight: 700; }}
    .metric-card p {{ margin: 8px 0 0 0; font-size: 13px; }}
    .info-callout {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 6px;
        border-left: 5px solid {HEX_VIBRANT_BLUE};
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# DATA PROCESSING ENGINE
# ---------------------------------------------------------------------------------
def process_sqp_dataframe(uploaded_file):
    df = pd.read_csv(uploaded_file, skiprows=1)
    
    # Ensure numeric types
    numeric_cols = [
        'Search Query Volume', 'Impressions: Total Count', 'Impressions: Brand Count', 'Impressions: Brand Share %',
        'Clicks: Total Count', 'Clicks: Click Rate %', 'Clicks: Brand Count', 'Clicks: Brand Share %',
        'Clicks: Price (Median)', 'Clicks: Brand Price (Median)', 'Cart Adds: Total Count', 'Cart Adds: Brand Count',
        'Cart Adds: Brand Share %', 'Purchases: Total Count', 'Purchases: Purchase Rate %', 'Purchases: Brand Count',
        'Purchases: Brand Share %', 'Purchases: Price (Median)', 'Purchases: Brand Price (Median)',
        'Clicks: Same Day Shipping Speed', 'Clicks: 1D Shipping Speed', 'Clicks: 2D Shipping Speed'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Advanced Derived Calculations
    df['Price_Premium_vs_Market'] = df['Clicks: Brand Price (Median)'] - df['Clicks: Price (Median)']
    df['Brand_Click_to_Cart_Rate'] = np.where(df['Clicks: Brand Count'] > 0, (df['Cart Adds: Brand Count'] / df['Clicks: Brand Count']) * 100, 0)
    df['Brand_Cart_to_Purchase_Rate'] = np.where(df['Cart Adds: Brand Count'] > 0, (df['Purchases: Brand Count'] / df['Cart Adds: Brand Count']) * 100, 0)
    
    return df

# ---------------------------------------------------------------------------------
# SIDEBAR CONTROL & UPLOAD CONTROLLER
# ---------------------------------------------------------------------------------
st.sidebar.markdown(f"<h2 style='color: {HEX_DEEP_BLUE}; margin-top: 0;'>📊 Amazon SQP Engine</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📤 Upload Amazon SQP Brand CSV File", 
    type=["csv"],
    help="Upload your standard raw Brand View Amazon Search Query Performance Report."
)

if not uploaded_file:
    st.info("👋 Welcome! Please upload your 'US_Search_Query_Performance_Brand_View' CSV file via the sidebar upload option to generate the complete visual engine.")
    st.stop()

# Data is ready
df = process_sqp_dataframe(uploaded_file)

# Dynamic Filter Controls
st.sidebar.markdown("### 🎛️ Dashboard Filters")
min_volume = st.sidebar.slider("Min Search Query Volume", int(df['Search Query Volume'].min()), int(df['Search Query Volume'].max()), 500)
search_query_input = st.sidebar.text_input("🔍 Text Filter Query (Regex / Substring)").lower()

# Apply filters
filtered_df = df[df['Search Query Volume'] >= min_volume]
if search_query_input:
    filtered_df = filtered_df[filtered_df['Search Query'].str.lower().str.contains(search_query_input)]

# ---------------------------------------------------------------------------------
# MASTER HEADER SECTION
# ---------------------------------------------------------------------------------
st.title("📊 Amazon Search Query Performance Brand Dashboard")
st.markdown("#### **Corporate Business Unit Insights Engine**")
st.markdown("---")

# Tab Layout Definition
tab_macro, tab_ppc, tab_leakage, tab_shipping = st.tabs([
    "📈 Macro Funnel Breakdown", 
    "🎯 PPC Target Discovery", 
    "🚨 Budget Wasted Spend & Leakage", 
    "🚚 Fulfillment Logistics Speed"
])

# ---------------------------------------------------------------------------------
# TAB 1: MACRO FUNNEL BREAKDOWN
# ---------------------------------------------------------------------------------
with tab_macro:
    st.subheader("📌 Funnel Conversion Executive Summary")
    
    # Calculate Macro Numbers
    tot_imp = filtered_df['Impressions: Total Count'].sum()
    br_imp = filtered_df['Impressions: Brand Count'].sum()
    imp_pct = (br_imp / tot_imp * 100) if tot_imp > 0 else 0
    
    tot_clk = filtered_df['Clicks: Total Count'].sum()
    br_clk = filtered_df['Clicks: Brand Count'].sum()
    clk_pct = (br_clk / tot_clk * 100) if tot_clk > 0 else 0
    
    tot_pur = filtered_df['Purchases: Total Count'].sum()
    br_pur = filtered_df['Purchases: Brand Count'].sum()
    pur_pct = (br_pur / tot_pur * 100) if tot_pur > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class='metric-card'>
            <h4>Impressions Pipeline</h4>
            <h2>{br_imp:,}</h2>
            <p style='color: {HEX_DEEP_BLUE}'>Brand Share: <b>{imp_pct:.2f}%</b></p>
            <small style='color: #95a5a6;'>Market Volume: {tot_imp:,}</small>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card' style='border-top-color: {HEX_VIBRANT_BLUE};'>
            <h4>Clicks Pipeline</h4>
            <h2>{br_clk:,}</h2>
            <p style='color: {HEX_VIBRANT_BLUE}'>Brand Share: <b>{clk_pct:.2f}%</b></p>
            <small style='color: #95a5a6;'>Market Volume: {tot_clk:,}</small>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='metric-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>Purchases Layer</h4>
            <h2>{br_pur:,}</h2>
            <p style='color: {HEX_DARK_SLATE}'>Brand Share: <b>{pur_pct:.2f}%</b></p>
            <small style='color: #95a5a6;'>Market Volume: {tot_pur:,}</small>
        </div>""", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Visual Layout
    c_left, c_right = st.columns([3, 2])
    with c_left:
        fig_funnel = go.Figure()
        fig_funnel.add_trace(go.Funnel(
            name='Total Market Funnel',
            y=['Impressions', 'Clicks', 'Purchases'],
            x=[tot_imp, tot_clk, tot_pur],
            textinfo="value+percent initial",
            marker=dict(color=[HEX_LIGHT_BLUE, HEX_DARK_SLATE, HEX_DEEP_BLUE])
        ))
        fig_funnel.update_layout(title="Full Attrition Pipeline Drop-off (Market)", template="plotly_white")
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with c_right:
        fig_pie_pur = go.Figure(data=[go.Pie(
            labels=['Brand Purchased Volume', 'Competitor Share'],
            values=[br_pur, tot_pur - br_pur],
            hole=.4,
            marker=dict(colors=[HEX_DEEP_BLUE, HEX_LIGHT_BLUE])
        )])
        fig_pie_pur.update_layout(title="Absolute Purchase Volume Market Share", template="plotly_white")
        st.plotly_chart(fig_pie_pur, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 2: PPC TARGET DISCOVERY
# ---------------------------------------------------------------------------------
with tab_ppc:
    st.subheader("🎯 High-Impact Opportunities & Campaign Segmentation")
    
    st.markdown(f"""<div class='info-callout'>
        <b>💡 Strategy Builder:</b> Conquesting focuses on high-volume terms where competitors control the market, while defense blocks competitors on core branded terms.
    </div>""", unsafe_allow_html=True)
    
    c_opp1, c_opp2 = st.columns(2)
    with c_opp1:
        st.markdown(f"<h4 style='color: {HEX_DEEP_BLUE};'>🔥 Top Conquesting Ad Targets (Brand Share < 5%)</h4>", unsafe_allow_html=True)
        conq = filtered_df[filtered_df['Purchases: Brand Share %'] < 5].sort_values(by='Search Query Volume', ascending=False).head(10)
        st.dataframe(conq[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Purchases: Brand Share %']], use_container_width=True)
        
    with c_opp2:
        st.markdown(f"<h4 style='color: {HEX_VIBRANT_BLUE};'>🛡️ Core Defensive Ad Strongholds (Brand Share > 40%)</h4>", unsafe_allow_html=True)
        defe = filtered_df[filtered_df['Purchases: Brand Share %'] >= 40].sort_values(by='Search Query Volume', ascending=False).head(10)
        st.dataframe(defe[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Purchases: Brand Share %']], use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Category Pricing Elasticity vs Conversion Volume")
    fig_bubble = px.scatter(
        filtered_df[filtered_df['Clicks: Brand Count'] > 0],
        x="Price_Premium_vs_Market",
        y="Purchases: Brand Share %",
        size="Search Query Volume",
        hover_name="Search Query",
        color_discrete_sequence=[HEX_DEEP_BLUE],
        title="Impact of Price Deviations on Absolute Brand Share",
        labels={"Price_Premium_vs_Market": "Price Premium vs Market Median ($)", "Purchases: Brand Share %": "Brand Purchase Share %"}
    )
    fig_bubble.update_layout(template="plotly_white")
    st.plotly_chart(fig_bubble, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 3: BUDGET WASTED SPEND & LEAKAGE
# ---------------------------------------------------------------------------------
with tab_leakage:
    st.subheader("🚨 Ad Spend Leakage Risk Assessment")
    
    st.markdown(f"""<div class='info-callout' style='border-left-color: crimson;'>
        <b>⚠️ Action Required:</b> Keywords with high brand clicks but absolute zero purchases indicate severe landing page friction, poor variant matching, or bad targeting. Add these as negatives.
    </div>""", unsafe_allow_html=True)
    
    leak = filtered_df[(filtered_df['Clicks: Brand Count'] >= 3) & (filtered_df['Purchases: Brand Count'] == 0)].sort_values(by='Clicks: Brand Count', ascending=False).head(15)
    
    if not leak.empty:
        st.dataframe(leak[['Search Query', 'Search Query Volume', 'Clicks: Brand Count', 'Cart Adds: Brand Count', 'Clicks: Brand Price (Median)']], use_container_width=True)
    else:
        st.success("🎉 Excellent! No ad spend leaks discovered matching current parameters.")
        
    st.markdown("---")
    st.subheader("📉 Drop-off Analysis: High Abandoned Carts")
    abandon_df = filtered_df[(filtered_df['Cart Adds: Brand Count'] > 1)].sort_values(by='Brand_Cart_to_Purchase_Rate', ascending=True).head(10)
    
    fig_bar = px.bar(
        abandon_df,
        x='Search Query',
        y='Brand_Cart_to_Purchase_Rate',
        title="Top 10 High Friction Keywords (Lowest Cart-to-Purchase Progression Rate)",
        color_discrete_sequence=[HEX_VIBRANT_BLUE]
    )
    fig_bar.update_layout(template="plotly_white")
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 4: FULFILLMENT LOGISTICS SPEED
# ---------------------------------------------------------------------------------
with tab_shipping:
    st.subheader("🚚 Fulfillment & Fast-Track Shipping Distribution")
    
    sd_clicks = filtered_df['Clicks: Same Day Shipping Speed'].sum()
    d1_clicks = filtered_df['Clicks: 1D Shipping Speed'].sum()
    d2_clicks = filtered_df['Clicks: 2D Shipping Speed'].sum()
    
    col_s1, col_s2 = st.columns([2, 3])
    with col_s1:
        fig_pie_ship = go.Figure(data=[go.Pie(
            labels=['Same Day Shipping', '1-Day Shipping', '2-Day Shipping'],
            values=[sd_clicks, d1_clicks, d2_clicks],
            marker=dict(colors=[HEX_DEEP_BLUE, HEX_VIBRANT_BLUE, HEX_LIGHT_BLUE])
        )])
        fig_pie_ship.update_layout(title="Click Distribution Across Shipping Tiers", template="plotly_white")
        st.plotly_chart(fig_pie_ship, use_container_width=True)
        
    with col_s2:
        st.markdown(f"""<div class='metric-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>📦 Operational Logistics Takeaway</h4>
            <p>Customer conversion velocity is directly tied to Prime eligibility speeds. When items fall out of regional distribution centers to 2-Day speeds, your brand conversion drop-off intensifies.</p>
            <ul>
                <li><b>Same Day Traffic Share:</b> { (sd_clicks / (sd_clicks+d1_clicks+d2_clicks)*100):.2f}%</li>
                <li><b>1-Day Express Share:</b> { (d1_clicks / (sd_clicks+d1_clicks+d2_clicks)*100):.2f}%</li>
                <li><b>2-Day Regular Share:</b> { (d2_clicks / (sd_clicks+d1_clicks+d2_clicks)*100):.2f}%</li>
            </ul>
        </div>""", unsafe_allow_html=True)
