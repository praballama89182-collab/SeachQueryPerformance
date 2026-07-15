import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------------
# 🎨 BRAND GRAPHICS, STYLING & PROFESSIONAL COLOR GRADING
# ---------------------------------------------------------------------------------
st.set_page_config(
    page_title="MerchantSpring | Advanced Amazon SQP Insights Engine",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color Grading Palette from Asset Specification
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
        color: {HEX_DARK_SLATE};
    }}
    .usecase-tag {{
        display: inline-block;
        background-color: {HEX_LIGHT_BLUE};
        color: {HEX_DARK_SLATE};
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------------
# ⚙️ ROBUST DATA ENGINE & PORTFOLIO INTELLIGENCE PIPELINE
# ---------------------------------------------------------------------------------
def process_amazon_sqp_data(file_obj):
    # Read CSV skipping Amazon's metadata metadata header row
    df = pd.read_csv(file_obj, skiprows=1)
    
    # Cast all numerical metrics cleanly to prevent aggregation breaks
    numeric_fields = [
        'Search Query Volume', 'Impressions: Total Count', 'Impressions: Brand Count', 'Impressions: Brand Share %',
        'Clicks: Total Count', 'Clicks: Click Rate %', 'Clicks: Brand Count', 'Clicks: Brand Share %',
        'Clicks: Price (Median)', 'Clicks: Brand Price (Median)', 'Cart Adds: Total Count', 'Cart Adds: Brand Count',
        'Cart Adds: Brand Share %', 'Purchases: Total Count', 'Purchases: Purchase Rate %', 'Purchases: Brand Count',
        'Purchases: Brand Share %', 'Purchases: Price (Median)', 'Purchases: Brand Price (Median)',
        'Clicks: Same Day Shipping Speed', 'Clicks: 1D Shipping Speed', 'Clicks: 2D Shipping Speed',
        'Cart Adds: Same Day Shipping Speed', 'Cart Adds: 1D Shipping Speed', 'Cart Adds: 2D Shipping Speed',
        'Purchases: Same Day Shipping Speed', 'Purchases: 1D Shipping Speed', 'Purchases: 2D Shipping Speed'
    ]
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            
    # Intent/Portfolio Segment Mapping Engine
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
    
    # Calculate Custom E-Commerce Progression Rates
    df['Brand_CTR'] = np.where(df['Impressions: Brand Count'] > 0, (df['Clicks: Brand Count'] / df['Impressions: Brand Count']) * 100, 0)
    df['Brand_Click_to_Cart_Rate'] = np.where(df['Clicks: Brand Count'] > 0, (df['Cart Adds: Brand Count'] / df['Clicks: Brand Count']) * 100, 0)
    df['Brand_Cart_to_Purchase_Rate'] = np.where(df['Cart Adds: Brand Count'] > 0, (df['Purchases: Brand Count'] / df['Cart Adds: Brand Count']) * 100, 0)
    
    return df

# ---------------------------------------------------------------------------------
# 🎛️ SIDEBAR CONTROL FRAMEWORK
# ---------------------------------------------------------------------------------
st.sidebar.markdown(f"<h2 style='color: {HEX_DEEP_BLUE}; margin-top: 0;'>🦅 Control Center</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📤 Drop Amazon SQP CSV Report", 
    type=["csv"],
    help="Directly drag and drop your raw Amazon Search Query Performance Brand View report here."
)

if not uploaded_file:
    st.info("💡 **Dashboard Engine Parked:** Please drag and drop your raw Amazon SQP CSV file into the sidebar uploader tool to activate the full 10-point analysis interface.")
    st.stop()

# Load Core Cleaned Data Frame
df = process_amazon_sqp_data(uploaded_file)

# Global Filters
st.sidebar.markdown("### 🔍 Live Scope Filters")
vol_threshold = st.sidebar.slider("Minimum Search Volume Filter", int(df['Search Query Volume'].min()), int(df['Search Query Volume'].max()), 100)
filtered_df = df[df['Search Query Volume'] >= vol_threshold]

# ---------------------------------------------------------------------------------
# 🏆 EXECUTIVE INTERFACE HEADER
# ---------------------------------------------------------------------------------
st.title("🏆 Amazon Search Query Performance Master Board")
st.markdown("### First-Party Brand Analytics Funnel & Market Share Control Center")
st.markdown("---")

# Distinct titles for all analysis sections split perfectly into structural tabs
tabs = st.tabs([
    "📈 1. Portfolio Market Share",
    "🎯 2. Sales Drivers & SEO Targets",
    "🚀 3. PPC Conquesting Opportunities",
    "🚨 4. Listing CTR Friction",
    "🛒 5. Checkout Conversion Gaps",
    "🚚 6. Supply Chain Logistics Speed"
])

# ---------------------------------------------------------------------------------
# TAB 1: BRAND MARKET POSITIONING
# ---------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("<span class='usecase-tag'>Use Case 7 & 10: Market Share & Business Intelligence</span>", unsafe_allow_html=True)
    st.subheader("🪐 Portfolio Share Mapping by Intent Segment")
    
    # Generate Cluster Aggregations
    seg_perf = filtered_df.groupby('Portfolio Segment').agg({
        'Search Query Volume': 'sum',
        'Impressions: Brand Count': 'sum',
        'Impressions: Total Count': 'sum',
        'Purchases: Brand Count': 'sum',
        'Purchases: Total Count': 'sum'
    }).reset_index()
    
    seg_perf['Absolute Market Purchase Share %'] = np.where(
        seg_perf['Purchases: Total Count'] > 0, 
        (seg_perf['Purchases: Brand Count'] / seg_perf['Purchases: Total Count']) * 100, 
        0
    )
    
    col_s1, col_s2, col_s3 = st.columns(3)
    def get_segment_share(name):
        subset = seg_perf[seg_perf['Portfolio Segment'] == name]
        return subset['Absolute Market Purchase Share %'].values[0] if not subset.empty else 0.0

    with col_s1:
        st.markdown(f"""<div class='kpi-card'>
            <h4>Kelp Category Dominance</h4>
            <h2>{get_segment_share('Kelp Cleanse Line'):.2f}%</h2>
            <p style='color: green;'>Primary Core Profit Engine</p>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_VIBRANT_BLUE};'>
            <h4>Oils & Omegas Share Capture</h4>
            <h2>{get_segment_share('Oils & Omega Supplements'):.2f}%</h2>
            <p style='color: red;'>Market Conquesting Vacuum</p>
        </div>""", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>Total Brand Orders Captured</h4>
            <h2>{int(filtered_df['Purchases: Brand Count'].sum())} Units</h2>
            <p style='color: {HEX_DEEP_BLUE};'>Across all Indexed Terms</p>
        </div>""", unsafe_allow_html=True)
        
    st.markdown("---")
    
    col_left, col_right = st.columns([3, 2])
    with col_left:
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
        fig_pos.update_layout(barmode='stack', title="Absolute Brand Performance vs Competitor Share", template="plotly_white")
        st.plotly_chart(fig_pos, use_container_width=True)
        
    with col_right:
        tot_pur = filtered_df['Purchases: Total Count'].sum()
        br_pur = filtered_df['Purchases: Brand Count'].sum()
        fig_pie_pur = go.Figure(data=[go.Pie(
            labels=['Brand Orders', 'Competitor Market Share'],
            values=[br_pur, tot_pur - br_pur],
            hole=.4,
            marker=dict(colors=[HEX_DEEP_BLUE, HEX_LIGHT_BLUE])
        )])
        fig_pie_pur.update_layout(title="Global Order Volume Breakout", template="plotly_white")
        st.plotly_chart(fig_pie_pur, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 2: SALES DRIVERS & SEO TARGETS
# ---------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("<span class='usecase-tag'>Use Case 1 & 3: Top Sales Drivers & SEO Listing Optimization</span>", unsafe_allow_html=True)
    st.subheader("💎 High-Yield Brand Strongholds & SEO Core Keywords")
    
    st.markdown("""<div class='strategic-box'>
        <b>📋 Action Item:</b> These search queries represent terms where your products are converting smoothly. Ensure these keywords are permanently embedded in your **Product Titles, Bullet Points, and Backend Search Terms** to secure organic ranking weights.
    </div>""", unsafe_allow_html=True)
    
    top_sales_df = filtered_df[filtered_df['Purchases: Brand Count'] > 0].sort_values(by='Purchases: Brand Count', ascending=False).head(15)
    
    st.dataframe(
        top_sales_df[['Search Query', 'Portfolio Segment', 'Search Query Volume', 'Purchases: Brand Count', 'Purchases: Brand Share %', 'Purchases: Brand Price (Median)']],
        use_container_width=True,
        column_config={
            "Search Query": "Indexed Search Keyword",
            "Portfolio Segment": "Product Line Group",
            "Search Query Volume": st.column_config.NumberColumn("Monthly Search Volume", format="%d"),
            "Purchases: Brand Count": st.column_config.NumberColumn("Brand Orders Placed", format="%d"),
            "Purchases: Brand Share %": st.column_config.NumberColumn("Brand Order Share %", format="%.2f%%"),
            "Purchases: Brand Price (Median)": st.column_config.NumberColumn("Your Price Point", format="$%.2f")
        }
    )

# ---------------------------------------------------------------------------------
# TAB 3: PPC CONQUESTING OPPORTUNITIES
# ---------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("<span class='usecase-tag'>Use Case 2 & 6: Missing Keyword Harvesting & Aggressive Bidding B2B/B2C</span>", unsafe_allow_html=True)
    st.subheader("🎯 High-Volume Conquesting Targets (Low Brand Share)")
    
    st.markdown("""<div class='strategic-box'>
        <b>📋 Strategy Protocol:</b> Shoppers are searching these keywords heavily, but your brand is currently captured under 5% of purchase transactions. Deploy these targets directly into **Sponsored Products Search-Only Manual Exact campaigns** with a top-of-search premium bid multiplier.
    </div>""", unsafe_allow_html=True)
    
    conq_df = filtered_df[(filtered_df['Search Query Volume'] >= 500) & (filtered_df['Purchases: Brand Share %'] < 5)].sort_values(by='Search Query Volume', ascending=False).head(15)
    
    st.dataframe(
        conq_df[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Clicks: Price (Median)', 'Purchases: Brand Share %']],
        use_container_width=True,
        column_config={
            "Search Query": "Conquesting Keyword Target",
            "Search Query Volume": st.column_config.NumberColumn("Search Volume Market Size", format="%d"),
            "Purchases: Total Count": st.column_config.NumberColumn("Total Segment Orders Available", format="%d"),
            "Clicks: Price (Median)": st.column_config.NumberColumn("Category Competitor Price", format="$%.2f"),
            "Purchases: Brand Share %": st.column_config.NumberColumn("Current Brand Share", format="%.2f%%")
        }
    )
    
    st.markdown("---")
    fig_bubble = px.scatter(
        conq_df,
        x="Search Query Volume",
        y="Purchases: Total Count",
        size="Purchases: Total Count",
        hover_name="Search Query",
        color_discrete_sequence=[HEX_VIBRANT_BLUE],
        title="High Velocity Category Traffic Gaps"
    )
    fig_bubble.update_layout(template="plotly_white")
    st.plotly_chart(fig_bubble, use_container_width=True)

# ---------------------------------------------------------------------------------
# TAB 4: LISTING CTR FRICTION
# ---------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("<span class='usecase-tag'>Use Case 4 & 9: Click-Through Rate & Listing Presentation Diagnostic</span>", unsafe_allow_html=True)
    st.subheader("🖱️ High Impression Count but Low Click Capture Optimization")
    
    st.markdown("""<div class='strategic-box' style='border-left-color: #3A414B;'>
        <b>⚠️ Listing Presentation Flag:</b> Your impressions are high but click rates are lagging behind category standards. This means your **Main Product Image, Listing Title, Coupon Badge, or Star-Rating Count** isn't turning window shoppers into active page visitors. Review listing creatives.
    </div>""", unsafe_allow_html=True)
    
    # Filter keywords with high impressions but low click share
    ctr_friction_df = filtered_df[(filtered_df['Impressions: Brand Count'] > 500) & (filtered_df['Clicks: Brand Share %'] < 5)].sort_values(by='Impressions: Brand Count', ascending=False).head(15)
    
    st.dataframe(
        ctr_friction_df[['Search Query', 'Impressions: Brand Count', 'Impressions: Brand Share %', 'Clicks: Brand Count', 'Clicks: Brand Share %']],
        use_container_width=True,
        column_config={
            "Search Query": "Search Term Terminus",
            "Impressions: Brand Count": st.column_config.NumberColumn("Brand Impressions Earned", format="%d"),
            "Impressions: Brand Share %": st.column_config.NumberColumn("Impression Share %", format="%.2f%%"),
            "Clicks: Brand Count": st.column_config.NumberColumn("Actual Brand Clicks", format="%d"),
            "Clicks: Brand Share %": st.column_config.NumberColumn("Click Share %", format="%.2f%%")
        }
    )

# ---------------------------------------------------------------------------------
# TAB 5: CHECKOUT CONVERSION GAPS
# ---------------------------------------------------------------------------------
with tabs[4]:
    st.markdown("<span class='usecase-tag'>Use Case 5 & 6: Conversion Gaps & Wasted Ad Spend Leakage</span>", unsafe_allow_html=True)
    st.subheader("🚨 Budget Alarms: Clicks without Purchases (Negative Match Isolation)")
    
    st.markdown("""<div class='strategic-box' style='border-left-color: crimson;'>
        <b>❌ Ad Spend Leakage Alert:</b> These keyword targets generated notable brand click traffic in June 2026 but resulted in <b>zero absolute purchases</b>. You are paying for ad clicks that fail to purchase. Action: Apply <b>Exact Negative Matches</b> immediately to save margin.
    </div>""", unsafe_allow_html=True)
    
    leakage_df = filtered_df[(filtered_df['Clicks: Brand Count'] >= 3) & (filtered_df['Purchases: Brand Count'] == 0)].sort_values(by='Clicks: Brand Count', ascending=False)
    
    if not leakage_df.empty:
        st.dataframe(
            leakage_df[['Search Query', 'Search Query Volume', 'Clicks: Brand Count', 'Cart Adds: Brand Count', 'Clicks: Brand Price (Median)']],
            use_container_width=True,
            column_config={
                "Search Query": "Wasted Traffic Term",
                "Search Query Volume": st.column_config.NumberColumn("Search Volume", format="%d"),
                "Clicks: Brand Count": st.column_config.NumberColumn("Wasted Clicks Paid", format="%d"),
                "Cart Adds: Brand Count": st.column_config.NumberColumn("Abandoned Cart Counts", format="%d"),
                "Clicks: Brand Price (Median)": st.column_config.NumberColumn("Your Mid Price Point", format="$%.2f")
            }
        )
    else:
        st.success("🎉 Safe Zone! No budget leak queries tracked above criteria.")

# ---------------------------------------------------------------------------------
# TAB 6: SUPPLY CHAIN LOGISTICS SPEED
# ---------------------------------------------------------------------------------
with tabs[5]:
    st.markdown("<span class='usecase-tag'>Use Case 8 & 10: Seasonality, Fulfillment Velocity & Inventory Constraints</span>", unsafe_allow_html=True)
    st.subheader("🚚 Customer Shipping Preference Distribution Curves")
    
    # Extract total fulfillment parameters
    sd_clicks = filtered_df['Clicks: Same Day Shipping Speed'].sum()
    d1_clicks = filtered_df['Clicks: 1D Shipping Speed'].sum()
    d2_clicks = filtered_df['Clicks: 2D Shipping Speed'].sum()
    
    col_l1, col_l2 = st.columns([2, 3])
    with col_l1:
        fig_ship_pie = go.Figure(data=[go.Pie(
            labels=['Same Day Delivery', '1-Day Shipping Express', '2-Day Standard Prime'],
            values=[sd_clicks, d1_clicks, d2_clicks],
            marker=dict(colors=[HEX_DEEP_BLUE, HEX_VIBRANT_BLUE, HEX_LIGHT_BLUE])
        )])
        fig_ship_pie.update_layout(title="Logistics Allocation Model", template="plotly_white")
        st.plotly_chart(fig_ship_pie, use_container_width=True)
        
    with col_l2:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>📦 Supply Chain & Inventory Warning</h4>
            <p>Customer conversion velocity is directly tied to FBA Prime distribution speeds. When inventory drops out of regional hubs down to standard 2-Day speeds, conversion drop-off spikes.</p>
            <ul>
                <li><b>Same Day Express Volume:</b> {sd_clicks:,} clicks</li>
                <li><b>1-Day Fast-Track Volume:</b> {d1_clicks:,} clicks</li>
                <li><b>2-Day Regular Volume:</b> {d2_clicks:,} clicks</li>
            </ul>
        </div>""", unsafe_allow_html=True)
