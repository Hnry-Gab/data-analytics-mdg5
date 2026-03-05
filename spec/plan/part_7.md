# PART 7: Dashboard & Testing

## Micro-Plan Objective
Develop a comprehensive Streamlit multi-page dashboard with interactive visualizations and implement comprehensive testing (unit tests, integration tests, E2E tests) to ensure reliability and production readiness.

---

## Dataframes Utilized + Schemas

### 1. Dashboard KPIs Summary Dataframe
```python
df_kpis = pd.DataFrame()
{
    'metric': str,                  # 'Total GMV', 'Total Orders', 'Unique Customers', etc.
    'value': float,
    'value_formatted': str,         # Formatted string for display (e.g., 'R$ 1.2M')
    'change_pct': float,            # Percentage change vs. previous period
    'change_abs': float,            # Absolute change vs. previous period
    'is_positive': bool,            # True if change is positive (green), False (red)
    'period': str                   # 'Current Period', 'Previous Period', 'All Time'
}
```

### 2. Time Series Aggregation Dataframe
```python
df_timeseries = pd.DataFrame()
{
    'date': datetime,               # Daily, weekly, or monthly aggregation
    'period_type': str,             # 'daily', 'weekly', 'monthly'
    'year': int,
    'month': int,
    'quarter': int,

    # Order metrics
    'n_orders': int,
    'n_customers': int,
    'avg_order_value': float,

    # Revenue metrics
    'gmv': float,                   # Gross Merchandise Value
    'total_freight': float,
    'net_revenue': float,           # GMV - returns/cancellations

    # Performance metrics
    'avg_delivery_delay_days': float,
    'on_time_delivery_rate': float,
    'avg_review_score': float,

    # Customer metrics
    'new_customers': int,
    'churned_customers': int,
    'churn_rate': float,
    'avg_clv': float
}
```

### 3. Geographic Aggregation Dataframe
```python
df_geo_agg = pd.DataFrame()
{
    'state': str,                   # 2-letter state code (SP, RJ, MG, etc.)
    'n_customers': int,
    'n_orders': int,

    # Revenue
    'gmv': float,
    'avg_order_value': float,

    # Performance
    'avg_delivery_delay_days': float,
    'avg_review_score': float,

    # Customer metrics
    'avg_recency': float,
    'avg_frequency': float,
    'avg_monetary': float,
    'churn_rate': float,
    'avg_clv': float,

    # Geo coordinates (for plotting)
    'latitude': float,              # State centroid latitude
    'longitude': float              # State centroid longitude
}
```

### 4. RFM Segment Summary Dataframe (Dashboard-ready)
```python
df_rfm_dashboard = pd.DataFrame()
{
    'rfm_segment': str,             # 'Champions', 'Loyal Customers', etc.
    'cluster_id': int,
    'n_customers': int,
    'pct_customers': float,         # Formatted as percentage

    # RFM characteristics
    'avg_recency': float,
    'avg_frequency': float,
    'avg_monetary': float,

    # Business metrics
    'total_gmv': float,
    'pct_gmv': float,
    'avg_clv': float,

    # Performance
    'avg_review_score': float,
    'churn_rate': float,

    # Color mapping
    'color': str                    # Hex color code for visualization
}
```

### 5. Churn Risk Summary Dataframe (Dashboard-ready)
```python
df_churn_dashboard = pd.DataFrame()
{
    'churn_risk_level': str,        # 'Low', 'Medium', 'High'
    'threshold': float,

    # Customer count
    'n_customers': int,
    'pct_customers': float,

    # Business value at risk
    'total_clv_at_risk': float,
    'avg_clv_per_customer': float,

    # Characteristics
    'avg_recency': float,
    'avg_frequency': float,
    'avg_monetary': float,
    'avg_review_score': float,

    # Actions
    'recommended_action': str,       # 'Monitor', 'Intervention', 'Priority Action'
    'color': str                    # Hex color code (green/yellow/red)
}
```

### 6. Attribution Analysis Dataframe
```python
df_attribution = pd.DataFrame()
{
    'dimension': str,               # 'payment_type', 'customer_state', 'product_category'
    'dimension_value': str,

    # Order metrics
    'n_orders': int,
    'pct_orders': float,

    # Revenue metrics
    'gmv': float,
    'pct_gmv': float,
    'avg_order_value': float,

    # Performance
    'avg_review_score': float,
    'avg_delivery_delay_days': float,
    'cancellation_rate': float,

    # Customer metrics
    'n_customers': int,
    'avg_clv': float,
    'churn_rate': float
}
```

### 7. Cohort Retention Dataframe
```python
df_cohort = pd.DataFrame()
{
    'cohort_month': str,             # Acquisition month (YYYY-MM)
    'cohort_index': int,            # 0, 1, 2, ... (months since acquisition)

    # Customer counts
    'n_customers': int,             # Customers in this cohort
    'n_retained': int,              # Customers still active in cohort_index month
    'retention_rate': float         # n_retained / n_customers
}
```

### 8. Top Products/Categories Dataframe
```python
df_top_products = pd.DataFrame()
{
    'rank': int,                    # 1, 2, 3, ... (ranking by GMV)
    'product_id': str,
    'product_category_name_english': str,

    # Sales metrics
    'n_orders': int,
    'n_items_sold': int,

    # Revenue
    'total_price': float,            # Sum of price
    'total_freight': float,
    'gmv': float,                   # total_price + total_freight
    'avg_price': float,
    'avg_freight': float,

    # Performance
    'avg_review_score': float,

    # Margin analysis
    'freight_ratio': float         # total_freight / gmv
}
```

### 9. Cross-Sell Recommendations Dataframe (Dashboard-ready)
```python
df_cross_sell_dashboard = pd.DataFrame()
{
    'customer_unique_id': str,
    'rfm_segment': str,
    'current_categories': list,      # Categories customer has purchased
    'recommended_category': str,
    'recommendation_score': float,

    # Rule details
    'rule_confidence': float,
    'rule_lift': float,
    'rule_support': float,

    # Expected impact
    'expected_clv_impact': float,
    'purchase_probability': float,

    # Display info
    'category_avg_price': float,
    'category_avg_review': float
}
```

---

## Dashboard Structure (Streamlit)

### app.py (Main Multi-Page Application)
```python
# Main Streamlit app structure
import streamlit as st

# Page navigation
st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar filters
st.sidebar.title("Filters")
date_range = st.sidebar.date_input("Date Range", [start_date, end_date])
states = st.sidebar.multiselect("States", all_states, default=all_states)
categories = st.sidebar.multiselect("Categories", all_categories, default=all_categories)

# Page navigation
PAGES = {
    "Overview": overview,
    "RFM Segmentation": rfm_segmentation,
    "CLV Analysis": clv_analysis,
    "Churn Prediction": churn_prediction,
    "Attribution": attribution
}

selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()
```

### pages/01_overview.py
```python
# Overview page components
# 1. KPI Cards (GMV, Orders, Customers, Avg Order Value, Review Score, On-Time Delivery)
# 2. Time Series Charts (GMV over time, Orders over time, Avg Review Score trend)
# 3. Geographic Choropleth Map (GMV by state, Customer count by state)
# 4. Top Products Table (Rank, Category, GMV, Orders, Avg Review)
# 5. Order Status Distribution Pie Chart (Delivered, Shipped, Canceled, etc.)
```

### pages/02_rfm.py
```python
# RFM Segmentation page components
# 1. 3D Scatter Plot (Recency x Frequency x Monetary, colored by segment)
# 2. RFM Segment Summary Table (Segment, Count, %, Avg R/F/M, GMV, Churn Rate)
# 3. RFM Segment Comparison Bar Chart (GMV, CLV, Review Score by segment)
# 4. Customer Segmentation Donut Chart (Count of customers per segment)
# 5. Segment Drill-down (Select segment to see customer list with details)
```

### pages/03_clv.py
```python
# CLV Analysis page components
# 1. CLV Distribution Histogram (Simple vs. BG/NBD comparison)
# 2. CLV Segment Comparison (High/Medium/Low CLV segments)
# 3. Top 25 Customers Table (Customer ID, Segment, CLV, Recency, Frequency, Monetary)
# 4. CLV Trend Chart (Predicted CLV over time by segment)
# 5. BG/NBD Alive Probability Scatter Plot (Alive Probability x Recency, size = Monetary)
```

### pages/04_churn.py
```python
# Churn Prediction page components
# 1. Churn Risk Distribution (Bar chart of Low/Medium/High risk counts)
# 2. Churn Risk Summary Table (Risk Level, Count, %, Total CLV at Risk, Recommended Action)
# 3. Feature Importance Chart (Top 10 features driving churn)
# 4. At-Risk Customers Table (Customer ID, Risk Level, Probability, RFM Segment, Review Score)
# 5. Churn by Segment Bar Chart (Churn rate per RFM segment)
```

### pages/05_attribution.py
```python
# Attribution page components
# 1. Payment Type Analysis (Bar chart: GMV by payment type)
# 2. Geographic Attribution (Map or bar chart: GMV, CLV, Churn by state)
# 3. Product Category Performance (Table: Category, GMV, Orders, Avg Review, Churn Rate)
# 4. Cohort Retention Heatmap (Cohort Month x Cohort Index, cell = retention rate)
# 5. Cross-Sell Recommendations (Table: Customer, Current Categories, Recommended Category, Score)
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Create Streamlit app shell with multi-page navigation and sidebar filters
   - [ ] Implement Overview page (01_overview.py) with KPIs, time series, geographic map
   - [ ] Build RFM Segmentation page (02_rfm.py) with 3D scatter plot and segment summary
   - [ ] Develop CLV Analysis page (03_clv.py) with distribution and top customers
   - [ ] Create Churn Prediction page (04_churn.py) with risk distribution and feature importance
   - [ ] Implement Attribution page (05_attribution.py) with payment, geographic, cohort analysis

   ## Medium Priority
   - [ ] Write comprehensive unit tests for dashboard components
   - [ ] Implement E2E tests with Playwright for critical user flows
   - [ ] Create Streamlit configuration (.streamlit/config.toml) with theme and performance settings
   - [ ] Add interactive filters (date range, state, category) to all pages
   - [ ] Implement data caching (@st.cache_data) for performance

   ## Low Priority
   - [ ] Add download functionality (CSV, PNG) for charts and tables
   - [ ] Create dashboard user guide and documentation
   - [ ] Implement real-time data refresh button

   ## Notes
   - Streamlit Configuration:
     * Primary color: Orange (#FF6B35) for brand consistency
     * Background: Light (#FFFFFF)
     * Secondary background: Light gray (#F0F2F6)
     * Text: Dark (#262730)
     * Font: Sans-serif (clean, readable)
     * Layout: Wide mode for better chart visibility
     * Caching: @st.cache_data with ttl=3600 (1 hour)
   - Visualization Libraries:
     * plotly.express: Interactive charts (scatter, line, bar, choropleth)
     * plotly.graph_objects: Advanced custom visualizations
     * streamlit.components.v1: Custom HTML components if needed
   - Page-Specific Components:
     * Overview:
       - KPI Cards: st.metric() with delta for change vs. previous period
       - Time Series: px.line() with interactive hover
       - Geographic Map: px.choropleth_mapbox or px.scatter_geo
       - Top Products: st.dataframe() with sorting
       - Order Status: px.pie()
     * RFM:
       - 3D Scatter: px.scatter_3d() (R, F, M axes)
       - Segment Summary: st.dataframe() with conditional formatting
       - Segment Comparison: px.bar() (grouped by segment)
       - Donut Chart: px.pie() with hole parameter
     * CLV:
       - Distribution: px.histogram() (Simple vs. BG/NBD overlay)
       - Top Customers: st.dataframe() with CLV sorting
       - Alive Probability: px.scatter() (color = segment, size = monetary)
     * Churn:
       - Risk Distribution: px.bar() (Low/Medium/High with color coding)
       - Feature Importance: px.bar() (horizontal, top 10 features)
       - At-Risk Table: st.dataframe() with risk level highlighting
     * Attribution:
       - Payment Analysis: px.bar() or px.sunburst()
       - Geographic: px.choropleth() or px.bar()
       - Cohort Heatmap: px.imshow() with annotations
   - Filters (Sidebar):
     * Date Range: st.date_input() (applies to time-based metrics)
     * States: st.multiselect() (default = all states)
     * Categories: st.multiselect() (default = all categories)
     * Segments: st.multiselect() (default = all RFM segments)
   - Caching Strategy:
     * Load data once: @st.cache_data
     * Filter data: Apply pandas operations after loading
     * Cache expensive computations (RFM, CLV, churn predictions)
   - Performance Optimization:
     * Use @st.cache_data decorator for data loading
     * Limit plotly figure size and interactivity for large datasets
     * Use sample datasets for testing (not full 100k rows)
   - E2E Testing with Playwright:
     * Test critical flows:
       1. Load overview page, verify KPIs display
       2. Navigate to RFM page, verify 3D scatter plot renders
       3. Apply filters (date range, state), verify data updates
       4. Navigate to Churn page, verify risk distribution shows
       5. Test interactive hover on charts
     * Use Playwright MCP for browser automation
     * Assert specific elements exist (KPI cards, charts, tables)
   - Unit Tests (pytest):
     * Test data loading functions (load_kpis, load_timeseries, etc.)
     * Test filter application logic
     * Test chart generation (verify Plotly figures created)
     * Test caching behavior (verify @st.cache_data works)
   - Documentation:
     * README.md with setup instructions (pip install requirements.txt)
     * Dashboard user guide: How to use each page and interpret metrics
     * Troubleshooting: Common issues and solutions
   - Edge Cases:
     * No data after filtering: Show "No data available" message
     * Large datasets: Use sampling or pagination for tables
     * Slow rendering: Show loading spinner with st.spinner()
     * Mobile view: Ensure charts are responsive
   - Accessibility:
     * Use high contrast colors
     * Add alt text to images/charts
     * Ensure font sizes are readable
   - Security:
     * No hardcoded credentials
     * Validate user inputs (filters)
     * Use environment variables for configuration
}
