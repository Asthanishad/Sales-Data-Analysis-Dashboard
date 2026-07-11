import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configurations
st.set_page_config(
    page_title="Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling for a premium look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .metric-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 5px solid #1f77b4;
    }
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1e3d59;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .sub-header {
        color: #17b978;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    
    # Try different encodings
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='windows-1252')
        
    # Standardize dates
    # Convert dates automatically
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
         
    # Feature Engineering
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Month Name'] = df['Order Date'].dt.strftime('%B')
    df['Quarter'] = 'Q' + df['Order Date'].dt.quarter.astype(str)
    df['Day'] = df['Order Date'].dt.day
    df['Profit Margin'] = df['Profit'] / df['Sales']
    df['Order Processing Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    if 'Row ID' in df.columns:
        df = df.drop(columns=['Row ID'])
        
    return df

# Initialize data
df = load_data("Sample - Superstore.csv")

if df is None:
    st.error("Error: 'Sample - Superstore.csv' file not found in the project directory. Please make sure the file is uploaded.")
else:
    # Sidebar Filtering Panel
    st.sidebar.markdown("# 📊 Sales Dashboard")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filter Dashboard Panel")
    
    # Year Filter
    years = sorted(df['Year'].dropna().unique())
    selected_years = st.sidebar.multiselect("Select Year", years, default=years)
    
    # Region Filter
    regions = sorted(df['Region'].dropna().unique())
    selected_regions = st.sidebar.multiselect("Select Region", regions, default=regions)
    
    # State Filter (Cascaded based on Region)
    if selected_regions:
        states = sorted(df[df['Region'].isin(selected_regions)]['State'].dropna().unique())
    else:
        states = sorted(df['State'].dropna().unique())
    selected_states = st.sidebar.multiselect("Select State", states, default=states)
    
    # Category Filter
    categories = sorted(df['Category'].dropna().unique())
    selected_categories = st.sidebar.multiselect("Select Category", categories, default=categories)
    
    # Segment Filter
    segments = sorted(df['Segment'].dropna().unique())
    selected_segments = st.sidebar.multiselect("Select Customer Segment", segments, default=segments)
    
    # Shipping Mode Filter
    ship_modes = sorted(df['Ship Mode'].dropna().unique())
    selected_ship_modes = st.sidebar.multiselect("Select Shipping Mode", ship_modes, default=ship_modes)
    
    # Apply Filters to DataFrame
    filtered_df = df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    if selected_states:
        filtered_df = filtered_df[filtered_df['State'].isin(selected_states)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    if selected_segments:
        filtered_df = filtered_df[filtered_df['Segment'].isin(selected_segments)]
    if selected_ship_modes:
        filtered_df = filtered_df[filtered_df['Ship Mode'].isin(selected_ship_modes)]
        
    # Main Header Section
    st.markdown("<h1 class='main-header'>📊 Sales Data Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("### Professional Business Intelligence & Data Operations Tool")
    st.markdown("---")
    
    # Metrics Row
    if not filtered_df.empty:
        total_sales = filtered_df['Sales'].sum()
        total_profit = filtered_df['Profit'].sum()
        profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
        total_orders = filtered_df['Order ID'].nunique()
        total_customers = filtered_df['Customer ID'].nunique()
        avg_order_val = total_sales / total_orders if total_orders > 0 else 0
        
        # Grid display using Columns
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(label="💰 Total Sales", value=f"${total_sales:,.2f}")
        with col2:
            st.metric(label="📈 Total Profit", value=f"${total_profit:,.2f}")
        with col3:
            st.metric(label="📊 Profit Margin", value=f"{profit_margin:.2f}%")
        with col4:
            st.metric(label="📦 Total Orders", value=f"{total_orders:,}")
        with col5:
            st.metric(label="👥 Total Customers", value=f"{total_customers:,}")
        with col6:
            st.metric(label="💳 Avg Order Value", value=f"${avg_order_val:,.2f}")
            
        st.markdown("---")
        
        # Tabs for Visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales & Profit Trends", "📦 Category & Product Analysis", "🌍 Geographical Performance", "⚙️ Logistics & Stats"])
        
        # Tab 1: Sales and Profit Trends
        with tab1:
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                st.markdown("#### Monthly Sales Trend")
                trend_sales = filtered_df.groupby('Order Date')['Sales'].sum().resample('ME').sum().reset_index()
                trend_sales['Order Date'] = trend_sales['Order Date'].dt.strftime('%Y-%m')
                fig_sales = px.line(trend_sales, x='Order Date', y='Sales', markers=True, title="Monthly Sales Over Time")
                fig_sales.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
                st.plotly_chart(fig_sales, use_container_width=True)
                
            with col_t2:
                st.markdown("#### Monthly Profit Trend")
                trend_profit = filtered_df.groupby('Order Date')['Profit'].sum().resample('ME').sum().reset_index()
                trend_profit['Order Date'] = trend_profit['Order Date'].dt.strftime('%Y-%m')
                fig_profit = px.line(trend_profit, x='Order Date', y='Profit', markers=True, title="Monthly Net Profit Over Time", color_discrete_sequence=['#2ca02c'])
                fig_profit.update_layout(xaxis_title="Month", yaxis_title="Profit ($)")
                st.plotly_chart(fig_profit, use_container_width=True)
                
            st.markdown("#### Yearly Performance Breakdown")
            yearly_perf = filtered_df.groupby('Year')[['Sales', 'Profit']].sum().reset_index()
            fig_yearly = px.bar(yearly_perf, x='Year', y=['Sales', 'Profit'], barmode='group', title="Year-on-Year Sales vs Profit comparison")
            st.plotly_chart(fig_yearly, use_container_width=True)
            
        # Tab 2: Category and Product Analysis
        with tab2:
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                st.markdown("#### Sales & Profit by Category")
                cat_data = filtered_df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
                fig_cat = px.bar(cat_data, x='Category', y='Sales', color='Profit', title="Category Sales Contribution and Net Profit", color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_cat, use_container_width=True)
                
            with col_p2:
                st.markdown("#### Treemap: Category and Sub-category Sales")
                fig_tree = px.treemap(filtered_df, path=['Category', 'Sub-Category'], values='Sales', color='Profit', color_continuous_scale='RdYlGn', title="Hierarchical Sales Structure")
                st.plotly_chart(fig_tree, use_container_width=True)
                
            col_p3, col_p4 = st.columns(2)
            
            with col_p3:
                st.markdown("#### Top 10 Most Profitable Products")
                top_p = filtered_df.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10).reset_index()
                fig_top_p = px.bar(top_p, x='Profit', y='Product Name', orientation='h', title="Top 10 Products by Profit", color='Profit', color_continuous_scale='Greens')
                fig_top_p.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top_p, use_container_width=True)
                
            with col_p4:
                st.markdown("#### Top 10 Profitable Customers")
                top_c = filtered_df.groupby('Customer Name')['Profit'].sum().sort_values(ascending=False).head(10).reset_index()
                fig_top_c = px.bar(top_c, x='Profit', y='Customer Name', orientation='h', title="Top 10 Customers by Profit", color='Profit', color_continuous_scale='Blues')
                fig_top_c.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top_c, use_container_width=True)
                
        # Tab 3: Geographical Performance
        with tab3:
            st.markdown("#### State-level Sales & Profit Mapping")
            state_data = filtered_df.groupby('State')[['Sales', 'Profit']].sum().reset_index()
            
            fig_state = px.bar(state_data.sort_values('Sales', ascending=False).head(20), x='State', y='Sales', color='Profit', 
                               title="Top 20 States by Sales and Profitability", color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_state, use_container_width=True)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("#### Regional Sales Distribution")
                reg_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
                fig_reg_s = px.pie(reg_sales, values='Sales', names='Region', hole=0.4, title="Regional Sales Contribution")
                st.plotly_chart(fig_reg_s, use_container_width=True)
            with col_g2:
                st.markdown("#### Regional Profit Distribution")
                reg_prof = filtered_df.groupby('Region')['Profit'].sum().reset_index()
                fig_reg_p = px.pie(reg_prof, values='Profit', names='Region', hole=0.4, title="Regional Profit Contribution", color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_reg_p, use_container_width=True)

        # Tab 4: Logistics & Stats
        with tab4:
            col_l1, col_l2 = st.columns(2)
            
            with col_l1:
                st.markdown("#### Order Shipping Mode Breakdown")
                ship_data = filtered_df.groupby('Ship Mode')['Order ID'].nunique().reset_index()
                fig_ship = px.pie(ship_data, values='Order ID', names='Ship Mode', title="Share of Orders by Shipping Mode")
                st.plotly_chart(fig_ship, use_container_width=True)
                
            with col_l2:
                st.markdown("#### Shipping Latency Distribution")
                fig_lat = px.histogram(filtered_df, x='Order Processing Days', nbins=10, title="Order Processing Latency (Days to Ship)", color_discrete_sequence=['orange'])
                st.plotly_chart(fig_lat, use_container_width=True)
                
            st.markdown("#### Correlation Heatmap (Sales, Quantity, Discount, Profit, Margin, Latency)")
            num_cols = filtered_df[['Sales', 'Quantity', 'Discount', 'Profit', 'Profit Margin', 'Order Processing Days']]
            corr_mat = num_cols.corr()
            fig_corr = px.imshow(corr_mat, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", title="Feature Correlation Matrix")
            st.plotly_chart(fig_corr, use_container_width=True)
            
    else:
        st.warning("No records match the selected filters. Please adjust the sidebar filter options.")
