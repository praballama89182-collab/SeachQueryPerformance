import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------------
# 🎨 COLOR PALETTE & LAYOUT CONFIGURATION
# ---------------------------------------------------------------------------------
st.set_page_config(
    page_title="Life Line | Executive Brand Positioning Board",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

HEX_BG = "#FBFBFC"
HEX_LIGHT_BLUE = "#D5DEE7"
HEX_DARK_SLATE = "#3A414B"
HEX_DEEP_BLUE = "#1652A3"
HEX_VIBRANT_BLUE = "#2F88F5"

st.markdown(f"""
    <style>
    .main {{ background-color: {HEX_BG}; }}
    .kpi-card {{
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(58, 65, 75, 0.06);
        border-top: 5px solid {HEX_DEEP_BLUE};
        margin-bottom: 20px;
    }}
    .kpi-card h4 {{ margin: 0 0 6px 0; color: #7f8c8d; font-size: 13px; text-transform: uppercase; letter-spacing: 0.8px; }}
    .kpi-card h2 {{ margin: 0; color: {HEX_DARK_SLATE}; font-size: 34px; font-weight: 800; }}
    .kpi-card p {{ margin: 8px 0 0 0; font-size: 14px; font-weight: 600; }}
    .strategic-box {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border-left: 6px solid {HEX_DEEP_BLUE};
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# ⚙️ ADVANCED DATA ENGINE
# ---------------------------------------------------------------------------------
def process_amazon_sqp_data(file_obj):
    df = pd.read_csv(file_obj, skiprows=1)
    
    # Cast formatting types safely
    numeric_fields = [
        'Search Query Volume', 'Impressions: Total Count', 'Impressions: Brand Count', 'Impressions: Brand Share %',
        'Clicks: Total Count', 'Clicks: Click Rate %', 'Clicks: Brand Count', 'Clicks: Brand Share %',
        'Clicks: Price (Median)', 'Clicks: Brand Price (Median)', 'Cart Adds: Total Count', 'Cart Adds: Brand Count',
        'Cart Adds: Brand Share %', 'Purchases: Total Count', 'Purchases: Purchase Rate %', 'Purchases: Brand Count',
        'Purchases: Brand Share %', 'Purchases: Price (Median)', 'Purchases: Brand Price (Median)',
        'Clicks: Same Day Shipping Speed', 'Clicks: 1D Shipping Speed', 'Clicks: 2D Shipping Speed'
    ]
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            
    # Portfolio Segmentation Engine
    def assign_portfolio_segment(query):
        query = str(query).lower()
        if 'kelp' in query:
            return 'Kelp Cleanse Line'
        elif 'oil' in query or 'omega' in query:
            return 'Oils & Omega Supplements'
        elif 'vitamin' in query or 'multivitamin' in query:
            return 'Vitamins & Minerals'
        else:
            return 'General Category Terms'

    df['Portfolio Segment'] = df['Search Query'].apply(assign_portfolio_segment)
    df['Price_Premium_vs_Market'] = df['Clicks: Brand Price (Median)'] - df['Clicks: Price (Median)']
    df['Conversion_Dropoff_Delta'] = df['Clicks: Brand Share %'] - df['Purchases: Brand Share %']
    
    return df

# ---------------------------------------------------------------------------------
# 🎛️ SIDEBAR UPLOAD CONTROL PANEL
# ---------------------------------------------------------------------------------
st.sidebar.markdown(f"<h2 style='color: {HEX_DEEP_BLUE}; margin-bottom: 0;'>🦅 Portfolio Control</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Upload raw SQP CSV Report", 
    type=["csv"],
    help="Directly drag and drop your raw Amazon Search Query Performance Brand report."
)

if not uploaded_file:
    st.info("💡 **Control Tower Active:** Please drop your raw Amazon SQP CSV file into the sidebar uploader to launch the interactive analytics engine.")
    st.stop()

# Load Core Data Frame
df = process_amazon_sqp_data(uploaded_file)

# Global Filters
st.sidebar.markdown("### 🔍 Granular Scope Filters")
vol_threshold = st.sidebar.slider("Minimum Search Volume Filter", int(df['Search Query Volume'].min()), int(df['Search Query Volume'].max()), 300)
filtered_df = df[df['Search Query Volume'] >= vol_threshold]

# ---------------------------------------------------------------------------------
# LAYOUT STRUCTURE & EXECUTIVE TABS
# ---------------------------------------------------------------------------------
st.title("🏆 Life Line Strategic Brand Positioning Board")
st.markdown("### Marketplace Intelligence Matrix | Executive Overview")
st.markdown("---")

tab_position, tab_capitalize, tab_leakage, tab_data = st.tabs([
    "📊 Brand Market Positioning", 
    "🎯 Capitalize: Growth Keywords", 
    "🚨 Margin Wasted Spend Leakage", 
    "📋 Raw Keyword Performance Grid"
])

# ---------------------------------------------------------------------------------
# TAB 1: BRAND MARKET POSITIONING
# ---------------------------------------------------------------------------------
with tab_position:
    st.subheader("🪐 Portfolio Share Mapping by Intent Segment")
    
    # Segment-level aggregates
    seg_perf = filtered_df.groupby('Portfolio Segment').agg({
        'Search Query Volume': 'sum',
        'Impressions: Brand Count': 'sum',
        'Impressions: Total Count': 'sum',
        'Purchases: Brand Count': 'sum',
        'Purchases: Total Count': 'sum'
    }).reset_index()
    seg_perf['Absolute Market Purchase Share %'] = (seg_perf['Purchases: Brand Count'] / seg_perf['Purchases: Total Count']) * 100
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""<div class='kpi-card'>
            <h4>Kelp Category Dominance</h4>
            <h2>{seg_perf.loc[seg_perf['Portfolio Segment']=='Kelp Cleanse Line', 'Absolute Market Purchase Share %'].values[0]:.2f}%</h2>
            <p style='color: green;'>Primary Profit Engine</p>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_VIBRANT_BLUE};'>
            <h4>Oils & Omegas Capture Share</h4>
            <h2>{seg_perf.loc[seg_perf['Portfolio Segment']=='Oils & Omega Supplements', 'Absolute Market Purchase Share %'].values[0]:.2f}%</h2>
            <p style='color: red;'>Market Conquesting Vacuum</p>
        </div>""", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>Total Brand Orders Captured</h4>
            <h2>{int(filtered_df['Purchases: Brand Count'].sum())} Units</h2>
            <p style='color: {HEX_DEEP_BLUE};'>Across all Indexed Terms</p>
        </div>""", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Visual Breakdown: Pure Position Bar Grid
    st.markdown("### 📈 Share Matrix: Absolute Brand Share vs Segment Market Size")
    
    fig_pos = go.Figure()
    fig_pos.add_trace(go.Bar(
        name='Brand Purchases Volume',
        x=seg_perf['Portfolio Segment'],
        y=seg_perf['Purchases: Brand Count'],
        marker_color=HEX_DEEP_BLUE
    ))
    fig_pos.add_trace(go.Bar(
        name='Total Competitor Volume',
        x=seg_perf['Portfolio Segment'],
        y=seg_perf['Purchases: Total Count'] - seg_perf['Purchases: Brand Count'],
        marker_color=HEX_LIGHT_BLUE
    ))
    fig_pos.update_layout(barmode='stack', title="Where Your Brand Owns the Segment vs Where Competitors Dominate", template="plotly_white")
    st.plotly_chart(fig_pos, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 2: CAPITALIZE: GROWTH KEYWORDS
# ---------------------------------------------------------------------------------
with tab_capitalize:
    st.subheader("🎯 Scalable Revenue Generation: High Volume Search Terms to Capitalize On")
    
    st.markdown(f"""<div class='strategic-box'>
        <b>📋 Execution Playbook:</b> These keywords represent huge category standard demand where your brand currently captures less than 5% of purchase share. Target these immediately inside new <b>Search-Only Manual campaigns (Exact Match)</b>. Do not run auto/semi-auto match variations here.
    </div>""", unsafe_allow_html=True)
    
    # Capitalize Filtering Logic: High Volume, Low Share
    cap_df = filtered_df[filtered_df['Purchases: Brand Share %'] < 5].sort_values(by='Search Query Volume', ascending=False).head(15)
    
    st.dataframe(
        cap_df[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Clicks: Price (Median)', 'Purchases: Brand Share %']],
        use_container_width=True,
        column_config={
            "Search Query": "Target Search Keyword",
            "Search Query Volume": st.column_config.NumberFormatter("Monthly Volume", format="%d"),
            "Purchases: Total Count": "Total Category Orders",
            "Clicks: Price (Median)": st.column_config.NumberFormatter("Category Median Price", format="$%.2f"),
            "Purchases: Brand Share %": st.column_config.NumberFormatter("Current Brand Share", format="%.2f%%")
        }
    )
    
    st.markdown("---")
    st.subheader("📊 Purchase Share Trajectory: Volume vs Brand Footprint")
    
    fig_cap = px.scatter(
        cap_df,
        x="Search Query Volume",
        y="Purchases: Total Count",
        size="Purchases: Total Count",
        hover_name="Search Query",
        color_discrete_sequence=[HEX_VIBRANT_BLUE],
        title="High Volume Scale Opportunities (Larger Bubbles = Higher Category Orders)"
    )
    fig_cap.update_layout(template="plotly_white")
    st.plotly_chart(fig_cap, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 3: MARGIN WASTED SPEND LEAKAGE
# ---------------------------------------------------------------------------------
with tab_leakage:
    st.subheader("🚨 Wasted Ad Spend & Conversion Leakage Vectors")
    
    st.markdown(f"""<div class='strategic-box' style='border-left-color: #3A414B;'>
        <b>⚠️ Budget Alarms:</b> Terms generating significant customer click volumes for your brand but returning <b>0 absolute sales</b>. You are paying for the traffic while the budget is leaking. Action: Apply <b>Exact Negative Matches</b> immediately.
    </div>""", unsafe_allow_html=True)
    
    leak_df = filtered_df[(filtered_df['Clicks: Brand Count'] >= 3) & (filtered_df['Purchases: Brand Count'] == 0)].sort_values(by='Clicks: Brand Count', ascending=False)
    
    if not leak_df.empty:
        st.dataframe(
            leak_df[['Search Query', 'Search Query Volume', 'Clicks: Brand Count', 'Cart Adds: Brand Count', 'Clicks: Brand Price (Median)']],
            use_container_width=True,
            column_config={
                "Search Query": "Wasted Click Keyword Term",
                "Clicks: Brand Count": "Wasted Brand Clicks Paid",
                "Cart Adds: Brand Count": "Cart Add Drop-offs",
                "Clicks: Brand Price (Median)": st.column_config.NumberFormatter("Your Selling Price", format="$%.2f")
            }
        )
    else:
        st.success("🎉 Portfolio Clean! No conversion ad leakages identified above thresholds.")
        
    st.markdown("---")
    st.subheader("📦 Interactive Shipping Profile Share")
    
    # Calculate Pie chart parameters for shipping speeds
    ship_sd = filtered_df['Clicks: Same Day Shipping Speed'].sum()
    ship_1d = filtered_df['Clicks: 1D Shipping Speed'].sum()
    ship_2d = filtered_df['Clicks: 2D Shipping Speed'].sum()
    
    fig_ship_pie = go.Figure(data=[go.Pie(
        labels=['Same Day Immediate Speed', '1-Day Express Prime', '2-Day Standard Prime'],
        values=[ship_sd, ship_1d, ship_2d],
        hole=.3,
        marker=dict(colors=[HEX_DEEP_BLUE, HEX_VIBRANT_BLUE, HEX_LIGHT_BLUE])
    )])
    fig_ship_pie.update_layout(title="Logistics Speed Constraints: What Customer Clicks Expect", template="plotly_white")
    st.plotly_chart(fig_ship_pie, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 4: RAW KEYWORD PERFORMANCE GRID
# ---------------------------------------------------------------------------------
with tab_data:
    st.subheader("📋 Comprehensive Performance Explorer")
    st.markdown("Use this raw explorer to filter down your entire data suite by search volume, pricing tiers, and brand share percentage points.")
    
    st.dataframe(filtered_df[[
        'Search Query', 'Portfolio Segment', 'Search Query Volume', 
        'Impressions: Brand Share %', 'Clicks: Brand Share %', 'Purchases: Brand Share %',
        'Clicks: Brand Price (Median)', 'Clicks: Price (Median)'
    ]], use_container_width=True)
