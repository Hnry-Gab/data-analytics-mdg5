# MACRO PLANNING - Olist E-Commerce Growth Analytics

## Final Objective
Develop a comprehensive customer intelligence and growth analytics platform for the Olist Brazilian E-Commerce dataset, enabling data-driven decisions for customer retention, lifetime value optimization, and revenue growth through advanced machine learning models and interactive visualizations.

---

## Dataset + Schema Definition

### Dataset Source
**Olist Brazilian E-Commerce Public Dataset by Olist** (Kaggle)
- Period: September 2016 - October 2018
- Dataset Size: ~100k orders, ~99k customers, ~1M total records across 8 files

### Core Tables (8 CSV files)

#### 1. olist_customers_dataset.csv (99,442 records)
```python
{
    'customer_id': str,           # Unique identifier per order
    'customer_unique_id': str,    # Unique identifier per customer (key for analysis)
    'customer_zip_code_prefix': int,
    'customer_city': str,
    'customer_state': str         # 2-letter state code (SP, RJ, MG, etc.)
}
```

#### 2. olist_orders_dataset.csv (99,442 records)
```python
{
    'order_id': str,
    'customer_id': str,           # FK to customers
    'order_status': str,          # delivered, shipped, processing, canceled, etc.
    'order_purchase_timestamp': datetime,
    'order_approved_at': datetime,
    'order_delivered_carrier_date': datetime,
    'order_delivered_customer_date': datetime,
    'order_estimated_delivery_date': datetime
}
```

#### 3. olist_order_items_dataset.csv (112,651 records)
```python
{
    'order_id': str,              # FK to orders
    'order_item_id': int,         # Sequential item number in order
    'product_id': str,            # FK to products
    'seller_id': str,             # FK to sellers
    'shipping_limit_date': datetime,
    'price': float,               # Item price
    'freight_value': float        # Shipping cost
}
```

#### 4. olist_order_payments_dataset.csv (103,887 records)
```python
{
    'order_id': str,              # FK to orders
    'payment_sequential': int,   # Payment sequence (multiple payment methods possible)
    'payment_type': str,          # credit_card, boleto, voucher, debit_card
    'payment_installments': int,  # Number of installments
    'payment_value': float        # Payment amount
}
```

#### 5. olist_order_reviews_dataset.csv (104,720 records)
```python
{
    'review_id': str,
    'order_id': str,              # FK to orders
    'review_score': int,          # 1-5 rating
    'review_comment_title': str,  # Optional text
    'review_comment_message': str, # Optional text (NLP target)
    'review_creation_date': datetime,
    'review_answer_timestamp': datetime
}
```

#### 6. olist_products_dataset.csv (32,952 records)
```python
{
    'product_id': str,
    'product_category_name': str,  # Portuguese category name
    'product_name_lenght': int,
    'product_description_lenght': int,
    'product_photos_qty': int,
    'product_weight_g': int,
    'product_length_cm': int,
    'product_height_cm': int,
    'product_width_cm': int
}
```

#### 7. olist_sellers_dataset.csv (3,096 records)
```python
{
    'seller_id': str,
    'seller_zip_code_prefix': int,
    'seller_city': str,
    'seller_state': str
}
```

#### 8. product_category_name_translation.csv (71 categories)
```python
{
    'product_category_name': str,      # Portuguese
    'product_category_name_english': str # English translation
}
```

### Master Order DataFrame Schema (after joins)
```python
{
    # Core order info
    'order_id': str,
    'customer_unique_id': str,
    'order_status': str,
    'order_purchase_timestamp': datetime,

    # Delivery metrics
    'order_approved_at': datetime,
    'order_delivered_carrier_date': datetime,
    'order_delivered_customer_date': datetime,
    'order_estimated_delivery_date': datetime,
    'delivery_delay_days': float,      # Derived: actual - estimated

    # Customer info
    'customer_state': str,
    'customer_city': str,

    # Order items
    'product_id': str,
    'seller_id': str,
    'product_category_name_english': str,
    'order_item_id': int,
    'price': float,
    'freight_value': float,
    'total_order_value': float,        # Derived: sum(price + freight)

    # Payment info
    'payment_type': str,
    'payment_installments': int,
    'payment_value': float,

    # Review info
    'review_score': int,
    'review_comment_message': str,
    'review_creation_date': datetime
}
```

---

## Analysis Techniques

### 1. Descriptive Analytics
- **RFM Analysis**: Recency, Frequency, Monetary value segmentation
- **Cohort Analysis**: Customer retention by acquisition month
- **Geographic Analysis**: Revenue, LTV, churn by state/city
- **Funnel Analysis**: Order status distribution and conversion rates

### 2. Predictive Analytics
- **Churn Prediction**: Probability of customer inactivity (>180 days)
- **CLV Prediction**: Customer Lifetime Value estimation
- **Order Prediction**: Next purchase timing and value

### 3. Causal Analytics
- **Uplift Modeling**: Identify customers responsive to incentives
- **Attribution Analysis**: Impact of reviews, delivery delay, payment type on conversion

### 4. NLP & Text Analytics
- **Sentiment Analysis**: Review comment sentiment (positive/negative/neutral)
- **Topic Modeling**: Discover themes in customer complaints/feedback
- **Text Preprocessing**: Tokenization, stemming, stopword removal (Portuguese)

### 5. Association Rule Mining
- **Cross-sell Analysis**: Market basket analysis for product recommendations
- **Apriori Algorithm**: Find frequent item sets and association rules

---

## Tech Stack

### Core Language & Data
- **Python 3.10+**
- **pandas**: Data manipulation and DataFrame operations
- **numpy**: Numerical computing and array operations
- **datetime**: Timestamp processing

### Machine Learning
- **scikit-learn**:
  - KMeans (clustering)
  - StandardScaler (feature scaling)
  - RandomForestClassifier (churn baseline)
  - train_test_split, metrics, pipelines
- **XGBoost/LightGBM**:
  - Gradient boosting for churn prediction
  - Feature importance analysis
- **lifetimes**:
  - Beta-Geometric/Negative Binomial Distribution (BG/NBD)
  - Gamma-Gamma model for CLV prediction
  - Probabilistic customer lifetime modeling

### Causal Inference
- **causalml**:
  - Uplift modeling (Meta-Learners)
  - Treatment effect estimation
  - Campaign response prediction

### NLP & Text Processing
- **nltk**:
  - Portuguese stopword removal
  - Tokenization
  - SnowballStemmer (Portuguese)
- **spacy**:
  - Advanced NLP pipeline (alternative to nltk)
  - Named entity recognition
  - Part-of-speech tagging

### Visualization & Dashboard
- **streamlit**: Interactive web dashboard
  - Multi-page application
  - Sidebar filters
  - Plotly charts
- **plotly**: Interactive visualizations
  - 3D scatter plots (RFM)
  - Choropleth maps (geographic)
  - Time series
- **seaborn**: Statistical visualizations
  - Heatmaps
  - Distribution plots
  - Correlation matrices

### Data Storage & Caching
- **parquet**: Efficient data serialization with snappy compression
- **@st.cache_data**: Streamlit caching for performance

### Testing & Quality Assurance
- **pytest**: Unit testing framework
- **pytest-cov**: Code coverage reporting
- **playwright** (MCP): End-to-end dashboard testing

### Development Tools
- **Git**: Version control
- **Jupyter Notebook**: Exploratory data analysis
- **nbconvert**: Export notebooks to HTML

---

## Prediction Models

### 1. Churn Prediction Model
**Objective**: Predict probability of customer churn (inactivity >180 days)

**Model**: XGBoost Classifier
- Features:
  - Recency (days since last purchase)
  - Frequency (number of purchases)
  - Monetary (total spend)
  - Average review score
  - Average delivery delay
  - Preferred payment type
  - Most purchased category
  - Customer state
- Target: `churn_flag` (1 if inactive >180 days, 0 otherwise)
- Evaluation: ROC-AUC, Precision, Recall, F1-Score
- Output: `churn_probability` (0-1)

### 2. CLV Prediction Model
**Objective**: Estimate Customer Lifetime Value

**Model A**: Simple CLV Formula
```
CLV = avg_order_value * purchase_frequency * 365
```

**Model B**: BG/NBD + Gamma-Gamma (Probabilistic)
- **BG/NBD Model**: Predicts future transactions
  - Frequency: Number of repeat purchases
  - Recency: Time since last purchase
  - T: Customer age (first purchase to reference date)
- **Gamma-Gamma Model**: Predicts monetary value per transaction
- Output: `expected_purchases` and `expected_clv` for next 90/180/365 days

### 3. Review Sentiment Model
**Objective**: Classify review sentiment

**Model**: NLP Pipeline
- Preprocessing:
  - Lowercase conversion
  - Stopword removal (Portuguese)
  - Tokenization
  - Stemming
- Features: TF-IDF vectors from review comments
- Model: Logistic Regression or Naive Bayes
- Evaluation: Accuracy, classification report
- Output: `sentiment_score` (-1 to 1)

### 4. Uplift Modeling (Causal Inference)
**Objective**: Identify customers responsive to interventions

**Model**: Two-Model Approach / CausalML Meta-Learners
- Treatment: Incentive/campaign exposure
- Control: No intervention
- Features: RFM, review history, delivery experience
- Outcome: Purchase behavior
- Output: `uplift_score` (incremental lift from treatment)

---

## Clustering Strategies

### 1. RFM Clustering (K-Means)
**Objective**: Segment customers based on purchasing behavior

**Features**:
- **Recency**: Days since last purchase (lower is better)
- **Frequency**: Number of purchases (higher is better)
- **Monetary**: Total spend (higher is better)

**Preprocessing**:
- Log transformation for skewed distributions
- StandardScaler (z-score normalization)
- Outlier handling (cap at 99th percentile)

**Algorithm**: K-Means Clustering
- n_clusters = 5 (optimal via Elbow Method + Silhouette Score)
- n_init = 10 (multiple initializations)
- random_state = 42 (reproducibility)

**Segment Labels**:
1. **Champions**: High R, High F, High M
2. **Loyal Customers**: High R, Medium-High F, High M
3. **Potential Loyalists**: High R, Low F, Medium M
4. **At Risk**: Low R, Medium F, Medium-High M
5. **Lost**: Low R, Low F, Low M

### 2. BG/NBD Segmentation (Probabilistic)
**Objective**: Predict future behavior using probabilistic models

**Segments** (based on CLV quantiles and churn probability):
1. **Valuable High-CLV**: Top 25% CLV, low churn risk
2. **Loyal Mid-CLV**: Middle 50% CLV, low churn risk
3. **Developing**: Lower CLV, moderate engagement
4. **At Risk**: Moderate CLV, high churn probability
5. **Lost/Hibernating**: Low CLV, high churn probability

### 3. Geographic Clustering
**Objective**: Group states by revenue and growth patterns

**Features**:
- Total GMV (Gross Merchandise Value)
- Average order value
- Customer count
- Average delivery delay
- Churn rate

**Algorithm**: Hierarchical Clustering or K-Means

### 4. Category-Based Clustering
**Objective**: Identify product categories with similar characteristics

**Features**:
- Price distribution
- Volume
- Average freight
- Average review score
- Return/cancellation rate

---

## Output Deliverables

### 1. Python Modules (src/)
- `config.py`: Configuration constants and paths
- `data_loader.py`: CSV ingestion and master order join
- `data_cleaner.py`: Missing values, outliers, timestamp parsing
- `feature_engineering.py`: RFM, CLV, churn labels, derived features
- `cache.py`: DataFrame parquet caching with decorators
- `models/rfm.py`: K-Means clustering
- `models/clv.py`: CLV calculation and BG/NBD
- `models/churn.py`: Churn prediction (XGBoost)
- `models/cross_sell.py`: Market basket analysis
- `models/bgnd.py`: BG/NBD probabilistic modeling
- `models/sentiment.py`: NLP sentiment analysis
- `attribution.py`: Geographic and payment attribution, cohort analysis

### 2. Jupyter Notebook (notebooks/)
- `olist_analysis.ipynb`: Complete EDA and model analysis
  - Data quality assessment
  - EDA visualizations
  - RFM analysis
  - CLV modeling
  - Churn prediction
  - Cross-sell analysis
  - Attribution insights
  - BG/NBD results

### 3. Streamlit Dashboard (dashboard/)
- `app.py`: Multi-page application shell
- `pages/01_overview.py`: KPIs, time series, geographic map
- `pages/02_rfm.py`: 3D RFM scatter, segment summary table
- `pages/03_clv.py`: CLV distribution, segment comparison, top customers
- `pages/04_churn.py`: Churn risk distribution, at-risk table, feature importance
- `pages/05_attribution.py`: Payment analysis, cohort heatmap, GMV by state

### 4. Tests (tests/)
- Unit tests for all modules
- Data validation tests
- Model prediction tests
- Dashboard component tests (E2E with Playwright)

### 5. Documentation
- `README.md`: Setup, usage, troubleshooting
- `macro.md`: This macro planning document
- `part_1.md` through `part_7.md`: Detailed micro planning for each implementation phase
- `.streamlit/config.toml`: Streamlit configuration (theme, performance)

---

## Implementation Phases Overview

The project is divided into **7 equal-density parts**, each with balanced complexity and workload:

1. **Part 1**: Data Pipeline Foundation - Ingestion, cleaning, and basic structure
2. **Part 2**: Customer Analytics Core - RFM analysis and feature engineering
3. **Part 3**: Segmentation Models - K-Means and BG/NBD clustering
4. **Part 4**: Value Prediction - CLV modeling and probabilistic estimation
5. **Part 5**: Churn Prediction - XGBoost model and feature engineering
6. **Part 6**: Advanced Analytics - NLP, cross-sell, causal inference (uplift)
7. **Part 7**: Dashboard & Testing - Streamlit app, E2E testing, documentation

Each part contains 5-7 medium-density tasks following the RALPH structure, ensuring consistent session complexity and optimal context management.
