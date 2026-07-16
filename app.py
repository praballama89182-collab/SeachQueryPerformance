import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# ---------------------------------------------------------------------------------
# 🎨 BRAND-AGNOSTIC GLOBAL THEME & PALETTE SETUP
# ---------------------------------------------------------------------------------
st.set_page_config(
    page_title="MerchantSpring | Advanced Amazon SQP & Catalog Engine",
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
# ⚙️ ROBUST DATA ENGINES
# ---------------------------------------------------------------------------------
def clean_numeric(series):
    """Clean percentage and currency strings into pure numeric floats."""
    if series.dtype == object:
        series = series.astype(str).str.replace(r'[%\$,]', '', regex=True)
    return pd.to_numeric(series, errors='coerce').fillna(0)


def extract_dynamic_segments(queries, num_clusters=3):
    """
    Scans the actual search queries dynamically, extracts the most 
    recurring keywords, and uses them to cluster queries.
    This avoids any future "0.00%" errors across different brands.
    """
    words = []
    stop_words = {'and', 'the', 'for', 'with', 'in', 'of', 'by', 'to', 'on', 'a', 'an', 'size', 'pack', 'set'}
    for q in queries.dropna().unique():
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', str(q).lower())
        words.extend([t for t in tokens if t not in stop_words])
    
    # Get the top frequent terms
    frequent_terms = [word for word, count in Counter(words).most_common(num_clusters)]
    
    def assign_segment(query):
        query_str = str(query).lower()
        
        # Priority Rule: Diaper Niche Specific mapping
        if any(x in query_str for x in ['swim', 'swimm', 'pool', 'water']):
            return 'Swim Diapers'
        elif any(x in query_str for x in ['bamboo', 'viscose', 'natural', 'organic', 'toes']):
            return 'Natural & Eco Diapers'
        elif 'diaper' in query_str:
            return 'Standard Diapers'
            
        # Dynamic Fallback Clustering rule for other categories/brands
        for term in frequent_terms:
            if term in query_str:
                return f"Cluster: {term.title()}"
        return 'General Search Terms'
        
    return assign_segment


def process_sqp_data(file_obj):
    df = pd.read_csv(file_obj, skiprows=1)
    df.columns = df.columns.str.strip()
    
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
            df[field] = clean_numeric(df[field])
            
    # Assign the dynamic classifier
    if 'Search Query' in df.columns:
        assign_fn = extract_dynamic_segments(df['Search Query'])
        df['Portfolio Segment'] = df['Search Query'].apply(assign_fn)
    else:
        df['Portfolio Segment'] = 'General Segment'
        
    df['Price_Premium_vs_Market'] = df['Clicks: Brand Price (Median)'] - df['Clicks: Price (Median)']
    df['Brand_CTR'] = np.where(df['Impressions: Brand Count'] > 0, (df['Clicks: Brand Count'] / df['Impressions: Brand Count']) * 100, 0)
    df['Brand_Cart_to_Purchase_Rate'] = np.where(df['Cart Adds: Brand Count'] > 0, (df['Purchases: Brand Count'] / df['Cart Adds: Brand Count']) * 100, 0)
    return df


def process_catalog_data(file_obj):
    df = pd.read_csv(file_obj, skiprows=1)
    df.columns = df.columns.str.strip()
    
    numeric_fields = [
        'Impressions: Impressions', 'Clicks: Clicks', 'Clicks: Click Rate (CTR)',
        'Cart Adds: Cart Adds', 'Purchases: Purchases', 'Purchases: Search Traffic Sales',
        'Purchases: Conversion Rate %', 'Impressions: Price (Median)'
    ]
    for field in numeric_fields:
        if field in df.columns:
            df[field] = clean_numeric(df[field])
    return df


# ---------------------------------------------------------------------------------
# 🎛️ SIDEBAR CONTROL FRAMEWORK
# ---------------------------------------------------------------------------------
st.sidebar.markdown(f"<h2 style='color: {HEX_DEEP_BLUE}; margin-top: 0;'>📥 Data Control</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

sqp_file = st.sidebar.file_uploader("1️⃣ Upload Brand SQP CSV Report", type=["csv"])
catalog_file = st.sidebar.file_uploader("2️⃣ Upload Catalog Performance CSV Report", type=["csv"])

if not sqp_file or not catalog_file:
    st.info("👋 **Console Parked:** Please upload your search data files to dynamic cluster category terms.")
    st.stop()

df_sqp = process_sqp_data(sqp_file)
df_cat = process_catalog_data(catalog_file)

# Dynamic volume threshold calculation to keep visual clean
st.sidebar.markdown("### 🔍 Live Scope Filters")
med_val = int(df_sqp['Search Query Volume'].median())
vol_threshold = st.sidebar.slider("Minimum Search Volume", int(df_sqp['Search Query Volume'].min()), int(df_sqp['Search Query Volume'].max()), min(100, med_val))
filtered_sqp = df_sqp[df_sqp['Search Query Volume'] >= vol_threshold]


# ---------------------------------------------------------------------------------
# 🏆 MASTER EXECUTIVE INTERFACE HEADER
# ---------------------------------------------------------------------------------
st.title("🦅 Multi-Dimensional Marketplace Performance Console")
st.markdown("### First-Party Brand Analytics Intersecting Keyword Funnels & ASIN Performance Matrices")
st.markdown("---")

tabs = st.tabs([
    "📊 1. Macro Portfolio Market Share",
    "🎯 2. Sales Drivers & SEO Strongholds",
    "🚀 3. PPC Conquesting Opportunities",
    "🚨 4. Listing CTR Friction Diagnostics",
    "🛒 5. Checkout Conversion Leakage",
    "📦 6. ASIN Catalog Performance Explorer",
    "🚚 7. Fulfillment Logistics Speeds"
])


# ---------------------------------------------------------------------------------
# TAB 1: MACRO PORTFOLIO MARKET SHARE
# ---------------------------------------------------------------------------------
with tabs[0]:
    st.markdown("<span class='usecase-tag'>Market Share Monitoring & Product Development Strategy</span>", unsafe_allow_html=True)
    st.subheader("🪐 Segment-Level Share Mapping by Market Intent Clusters")
    
    seg_perf = filtered_sqp.groupby('Portfolio Segment').agg({
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
    
    # Sort and gather the top performance clusters
    sorted_segments = seg_perf.sort_values(by='Purchases: Brand Count', ascending=False)
    
    top_cluster_1 = sorted_segments.iloc[0]['Portfolio Segment'] if len(sorted_segments) > 0 else "N/A"
    top_cluster_2 = sorted_segments.iloc[1]['Portfolio Segment'] if len(sorted_segments) > 1 else "N/A"

    def get_segment_share(name):
        if name == "N/A": return 0.0
        subset = seg_perf[seg_perf['Portfolio Segment'] == name]
        return subset['Absolute Market Purchase Share %'].values[0] if not subset.empty else 0.0

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""<div class='kpi-card'>
            <h4>{top_cluster_1} Dominance</h4>
            <h2>{get_segment_share(top_cluster_1):.2f}%</h2>
            <p style='color: green;'>Primary Core Profit Engine</p>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_VIBRANT_BLUE};'>
            <h4>{top_cluster_2} Capture Share</h4>
            <h2>{get_segment_share(top_cluster_2):.2f}%</h2>
            <p style='color: #E74C3C;'>Market Growth Focus Segment</p>
        </div>""", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>Total Brand Orders Captured</h4>
            <h2>{int(filtered_sqp['Purchases: Brand Count'].sum()):,} Units</h2>
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
        fig_pos.update_layout(barmode='stack', title="Absolute Brand Performance Share vs Competitors", template="plotly_white")
        st.plotly_chart(fig_pos, use_container_width=True)
        
    with col_right:
        tot_pur = filtered_sqp['Purchases: Total Count'].sum()
        br_pur = filtered_sqp['Purchases: Brand Count'].sum()
        fig_pie_pur = go.Figure(data=[go.Pie(
            labels=['Brand Active Volume', 'Competitor Category Share'],
            values=[br_pur, max(0, tot_pur - br_pur)],
            hole=.4,
            marker=dict(colors=[HEX_DEEP_BLUE, HEX_LIGHT_BLUE])
        )])
        fig_pie_pur.update_layout(title="Global Order Market Share Allocation", template="plotly_white")
        st.plotly_chart(fig_pie_pur, use_container_width=True)


# ---------------------------------------------------------------------------------
# TAB 2: SALES DRIVERS & SEO STRONGHOLDS
# ---------------------------------------------------------------------------------
with tabs[1]:
    st.markdown("<span class='usecase-tag'>Top Search Queries Driving Sales & Visibility Expansion</span>", unsafe_allow_html=True)
    st.subheader("💎 High-Yield Brand Organic Strongholds & Core SEO Placement Terms")
    
    st.markdown("""<div class='strategic-box'>
        <b>📋 Execution Playbook:</b> These keywords represent search queries where your brand is successfully indexing and capturing real orders. Protect these aggressively by ensuring they are woven deeply into your **listing Titles, Bullet Points, and Backend Search Keywords**.
    </div>""", unsafe_allow_html=True)
    
    top_sales_df = filtered_sqp[filtered_sqp['Purchases: Brand Count'] > 0].sort_values(by='Purchases: Brand Count', ascending=False).head(15)
    
    st.dataframe(
        top_sales_df[['Search Query', 'Portfolio Segment', 'Search Query Volume', 'Purchases: Brand Count', 'Purchases: Brand Share %', 'Purchases: Brand Price (Median)']],
        use_container_width=True,
        column_config={
            "Search Query": "Indexed Search Keyword",
            "Portfolio Segment": "Product Cluster Category",
            "Search Query Volume": st.column_config.NumberColumn("Monthly Search Volume", format="%d"),
            "Purchases: Brand Count": st.column_config.NumberColumn("Brand Orders Confirmed", format="%d"),
            "Purchases: Brand Share %": st.column_config.NumberColumn("Your Order Share %", format="%.2f%%"),
            "Purchases: Brand Price (Median)": st.column_config.NumberColumn("Your Price Point", format="$%.2f")
        }
    )


# ---------------------------------------------------------------------------------
# TAB 3: PPC CONQUESTING OPPORTUNITIES
# ---------------------------------------------------------------------------------
with tabs[2]:
    st.markdown("<span class='usecase-tag'>Missing Keyword Discovery & Campaign Bid Optimization</span>", unsafe_allow_html=True)
    st.subheader("🎯 High-Volume Conquesting Ad Group Targets (Low Share Gaps)")
    
    st.markdown("""<div class='strategic-box'>
        <b>📋 PPC Protocol:</b> High search volume fields where your products hold under 5% market share. Launch clean **Sponsored Products Search-Only Manual Exact campaigns** for these targets immediately. Do not bleed ad dollars via semi-auto targeting vectors here.
    </div>""", unsafe_allow_html=True)
    
    conq_df = filtered_sqp[(filtered_sqp['Search Query Volume'] >= 500) & (filtered_sqp['Purchases: Brand Share %'] < 5)].sort_values(by='Search Query Volume', ascending=False).head(15)
    
    st.dataframe(
        conq_df[['Search Query', 'Search Query Volume', 'Purchases: Total Count', 'Clicks: Price (Median)', 'Purchases: Brand Share %']],
        use_container_width=True,
        column_config={
            "Search Query": "Target Conquesting Keyword",
            "Search Query Volume": st.column_config.NumberColumn("Total Search Volume Size", format="%d"),
            "Purchases: Total Count": st.column_config.NumberColumn("Total Segment Market Orders", format="%d"),
            "Clicks: Price (Median)": st.column_config.NumberColumn("Category Competitor Median Price", format="$%.2f"),
            "Purchases: Brand Share %": st.column_config.NumberColumn("Your Purchase Share %", format="%.2f%%")
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
# TAB 4: LISTING CTR FRICTION DIAGNOSTICS
# ---------------------------------------------------------------------------------
with tabs[3]:
    st.markdown("<span class='usecase-tag'>Listing Presentation & Click-Through Rate Optimization</span>", unsafe_allow_html=True)
    st.subheader("🖱️ High Impression Count with Depressed Click Capture Rates")
    
    st.markdown("""<div class='strategic-box' style='border-left-color: #3A414B;'>
        <b>⚠️ CTR Friction Alert:</b> Your listings are rendering impressions but failing to generate the corresponding volume of click traffic. Shoppers see your offer but skip past it. Review your **Main Image asset quality, Listing Title Clarity, or review rating differentials** vs competitors.
    </div>""", unsafe_allow_html=True)
    
    ctr_friction_df = filtered_sqp[(filtered_sqp['Impressions: Brand Count'] > 100) & (filtered_sqp['Clicks: Brand Share %'] < 5)].sort_values(by='Impressions: Brand Count', ascending=False).head(15)
    
    st.dataframe(
        ctr_friction_df[['Search Query', 'Impressions: Brand Count', 'Impressions: Brand Share %', 'Clicks: Brand Count', 'Clicks: Brand Share %']],
        use_container_width=True,
        column_config={
            "Search Query": "Search Term",
            "Impressions: Brand Count": st.column_config.NumberColumn("Brand Impressions", format="%d"),
            "Impressions: Brand Share %": st.column_config.NumberColumn("Impression Share %", format="%.2f%%"),
            "Clicks: Brand Count": st.column_config.NumberColumn("Brand Click Traffic", format="%d"),
            "Clicks: Brand Share %": st.column_config.NumberColumn("Click Share %", format="%.2f%%")
        }
    )


# ---------------------------------------------------------------------------------
# TAB 5: CHECKOUT CONVERSION LEAKAGE
# ---------------------------------------------------------------------------------
with tabs[4]:
    st.markdown("<span class='usecase-tag'>Fixing Funnel Conversion Gaps & Stopping Ad Leakage</span>", unsafe_allow_html=True)
    st.subheader("🚨 Budget Wasted Spend Neutralizer: Clicks without Purchases")
    
    st.markdown("""<div class='strategic-box' style='border-left-color: crimson;'>
        <b>❌ Ad Margin Bleed Warning:</b> Keywords generating significant paid click costs but returning **0 absolute sales**. Action: Map these terms directly into your **PPC campaigns as Negative Exact matches** immediately to rescue operating capital.
    </div>""", unsafe_allow_html=True)
    
    leakage_df = filtered_sqp[(filtered_sqp['Clicks: Brand Count'] >= 3) & (filtered_sqp['Purchases: Brand Count'] == 0)].sort_values(by='Clicks: Brand Count', ascending=False)
    
    if not leakage_df.empty:
        st.dataframe(
            leakage_df[['Search Query', 'Search Query Volume', 'Clicks: Brand Count', 'Cart Adds: Brand Count', 'Clicks: Brand Price (Median)']],
            use_container_width=True,
            column_config={
                "Search Query": "High Leakage Search Query",
                "Search Query Volume": st.column_config.NumberColumn("Search Volume", format="%d"),
                "Clicks: Brand Count": st.column_config.NumberColumn("Wasted Clicks Paid", format="%d"),
                "Cart Adds: Brand Count": st.column_config.NumberColumn("Abandoned Carts", format="%d"),
                "Clicks: Brand Price (Median)": st.column_config.NumberColumn("Your Selling Price", format="$%.2f")
            }
        )
    else:
        st.success("🎉 Safe Zone! No budget leak queries tracked above current filtering criteria.")


# ---------------------------------------------------------------------------------
# TAB 6: ASIN CATALOG PERFORMANCE EXPLORER
# ---------------------------------------------------------------------------------
with tabs[5]:
    st.markdown("<span class='usecase-tag'>Tactical Product Optimization (ASIN View Detail)</span>", unsafe_allow_html=True)
    st.subheader("📦 Product Catalog Conversion Metric Performance Grid")
    
    st.markdown("""<div class='strategic-box'>
        <b>📋 ASIN Diagnostic Matrix Guide:</b>
        *   <b>High Click Count + Deflated Conversion Rate %:</b> Listing detail friction. Add A+ Content, run clip-on vouchers, or address review objections.
        *   <b>Top Tier Conversion Rate % + Deflated Impressions:</b> High intent hero. Boost targeted exact PPC visibility to scale traffic velocity.
    </div>""", unsafe_allow_html=True)
    
    sorted_catalog = df_cat.sort_values(by='Purchases: Search Traffic Sales', ascending=False)
    
    st.dataframe(
        sorted_catalog[['ASIN Title', 'ASIN', 'Impressions: Impressions', 'Clicks: Clicks', 'Clicks: Click Rate (CTR)', 'Purchases: Purchases', 'Purchases: Conversion Rate %', 'Purchases: Search Traffic Sales', 'Impressions: Price (Median)']],
        use_container_width=True,
        column_config={
            "ASIN Title": "Amazon Product Title",
            "ASIN": "Amazon Catalog ASIN ID",
            "Impressions: Impressions": st.column_config.NumberColumn("Impressions Earned", format="%d"),
            "Clicks: Clicks": st.column_config.NumberColumn("Clicks Tracked", format="%d"),
            "Clicks: Click Rate (CTR)": st.column_config.NumberColumn("ASIN CTR %", format="%.2f%%"),
            "Purchases: Purchases": st.column_config.NumberColumn("Units Ordered", format="%d"),
            "Purchases: Conversion Rate %": st.column_config.NumberColumn("Product Conversion Rate", format="%.2f%%"),
            "Purchases: Search Traffic Sales": st.column_config.NumberColumn("Search Sales Revenue", format="$%.2f"),
            "Impressions: Price (Median)": st.column_config.NumberColumn("Median Sales Price", format="$%.2f")
        }
    )
    
    st.markdown("---")
    
    fig_cat_bar = px.bar(
        sorted_catalog.head(10),
        x='ASIN',
        y='Purchases: Search Traffic Sales',
        color='Purchases: Conversion Rate %',
        title="Top 10 ASIN Sales Drivers by Search Revenue (Color Depth Signals Unit CVR % Performance)",
        color_continuous_scale=[HEX_LIGHT_BLUE, HEX_VIBRANT_BLUE, HEX_DEEP_BLUE],
        labels={'Purchases: Search Traffic Sales': 'Search Sales Revenue ($)', 'Purchases: Conversion Rate %': 'CVR %'}
    )
    fig_cat_bar.update_layout(template="plotly_white")
    st.plotly_chart(fig_cat_bar, use_container_width=True)


# ---------------------------------------------------------------------------------
# TAB 7: FULFILLMENT LOGISTICS SPEEDS
# ---------------------------------------------------------------------------------
with tabs[6]:
    st.markdown("<span class='usecase-tag'>Fulfillment Distribution & Seasonality Safeguards</span>", unsafe_allow_html=True)
    st.subheader("🚚 Platform Shipping Speed Velocity Distributions")
    
    sd_clicks = filtered_sqp['Clicks: Same Day Shipping Speed'].sum()
    d1_clicks = filtered_sqp['Clicks: 1D Shipping Speed'].sum()
    d2_clicks = filtered_sqp['Clicks: 2D Shipping Speed'].sum()
    
    col_l1, col_l2 = st.columns([2, 3])
    with col_l1:
        fig_ship_pie = go.Figure(data=[go.Pie(
            labels=['Same Day Fast-Track', '1-Day Express Shipping', '2-Day Standard Delivery'],
            values=[sd_clicks, d1_clicks, d2_clicks],
            hole=.3,
            marker=dict(colors=[HEX_DEEP_BLUE, HEX_VIBRANT_BLUE, HEX_LIGHT_BLUE])
        )])
        fig_ship_pie.update_layout(title="Logistics Allocation Breakout Chart", template="plotly_white")
        st.plotly_chart(fig_ship_pie, use_container_width=True)
        
    with col_l2:
        st.markdown(f"""<div class='kpi-card' style='border-top-color: {HEX_DARK_SLATE};'>
            <h4>📦 FBA Inventory Regional Positioning Takeaway</h4>
            <p>Customer acquisition conversion metrics are directly correlated with FBA warehouse distribution levels. When regional out-of-stocks force delivery estimates out to standard 2-Day speeds, your funnel acquisition efficiency drops significantly.</p>
            <ul>
                <li><b>Same Day Delivery Traffic Size:</b> {sd_clicks:,.0f} clicks</li>
                <li><b>1-Day Prime Express Traffic Size:</b> {d1_clicks:,.0f} clicks</li>
                <li><b>2-Day Regular Shipping Traffic Size:</b> {d2_clicks:,.0f} clicks</li>
            </ul>
        </div>""", unsafe_allow_html=True)
