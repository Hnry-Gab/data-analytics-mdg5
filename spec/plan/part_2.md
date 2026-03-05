# PART 2: Customer Analytics Core

## Micro-Plan Objective
Develop comprehensive customer intelligence features including RFM analysis, churn labeling, and derived metrics that form the foundation for all segmentation and prediction models.

---

## Dataframes Utilized + Schemas

### 1. Customer-Level Aggregated Dataframe
```python
df_customers_agg = pd.DataFrame()
{
    'customer_unique_id': str,              # Primary key
    'customer_city': str,
    'customer_state': str,

    # Recency metrics
    'first_purchase_date': datetime,
    'last_purchase_date': datetime,
    'recency_days': float,                  # Days since last purchase (to REFERENCE_DATE)
    'customer_age_days': float,             # Days since first purchase

    # Frequency metrics
    'order_count': int,                     # Total number of orders
    'total_items': int,                      # Total items purchased
    'unique_products': int,                 # Number of unique products purchased

    # Monetary metrics
    'total_spend': float,                   # Sum of (price + freight_value)
    'avg_order_value': float,               # total_spend / order_count
    'avg_item_value': float,                # total_spend / total_items
    'avg_freight_value': float,             # Sum(freight_value) / order_count

    # Engagement metrics
    'avg_payment_installments': float,
    'preferred_payment_type': str,
    'most_purchased_category': str,
    'avg_review_score': float,              # Avg of review_score (1-5)
    'has_low_review': bool,                 # True if any review_score <= 2
    'review_count': int,

    # Delivery experience
    'avg_delivery_delay_days': float,       # Avg of (delivered_customer_date - estimated_delivery_date)
    'has_late_delivery': bool,              # True if any delivery_delay_days > 0
    'on_time_delivery_rate': float,         # Rate of on-time deliveries

    # Churn label
    'last_order_status': str,
    'is_churned': bool,                     # True if inactive > CHURN_THRESHOLD_DAYS
    'churn_risk_score': float               # Derived probability (0-1)
}
```

### 2. RFM Base Dataframe (Untransformed)
```python
df_rfm_raw = pd.DataFrame()
{
    'customer_unique_id': str,
    'recency': float,       # Days since last purchase (lower is better)
    'frequency': int,        # Number of purchases (higher is better)
    'monetary': float       # Total spend (higher is better)
}
```

### 3. RFM Transformed Dataframe (for K-Means)
```python
df_rfm_transformed = pd.DataFrame()
{
    'customer_unique_id': str,
    'recency_log': float,           # Log-transformed recency
    'frequency_log': float,         # Log-transformed frequency
    'monetary_log': float,          # Log-transformed monetary
    'recency_scaled': float,        # Z-score normalized
    'frequency_scaled': float,      # Z-score normalized
    'monetary_scaled': float        # Z-score normalized
}
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Implement customer aggregation logic in feature_engineering.py
   - [ ] Create RFM calculation with proper reference date handling
   - [ ] Develop churn labeling logic with configurable threshold (CHURN_THRESHOLD_DAYS = 180)
   - [ ] Build derived metrics pipeline (delivery delay, order value, engagement scores)
   - [ ] Implement RFM transformation (log + scaling) for clustering preparation

   ## Medium Priority
   - [ ] Add customer lifetime and cohort features (acquisition month, cohort retention)
   - [ ] Create unit tests for feature_engineering module (RFM, churn, derived metrics)
   - [ ] Implement data quality validation (negative values, impossible dates, outlier detection)

   ## Low Priority
   - [ ] Add advanced customer behavior features (repeat purchase rate, category diversity)
   - [ ] Create customer journey timeline extraction for analysis

   ## Notes
   - RFM calculation must use REFERENCE_DATE = '2018-10-17' (max date in orders dataset)
   - Churn definition: No purchase in last 180 days from reference date (96% of customers have only 1 purchase)
   - Log transformation: Use np.log1p() to handle zeros gracefully (log(x+1))
   - StandardScaler: Fit on training data only, apply same transformation to new data
   - Derived metrics:
     * delivery_delay_days = order_delivered_customer_date - order_estimated_delivery_date
     * avg_order_value = total_spend / order_count
     * on_time_delivery_rate = count(delivery_delay_days <= 0) / total_deliveries
   - Handle edge cases:
     * Customers with no reviews: avg_review_score = np.nan, review_count = 0
     * Customers with no deliveries: avg_delivery_delay_days = np.nan
     * Single-purchase customers: frequency = 1 (not 0)
   - Unit tests must verify:
     * RFM calculations match manual calculations for sample customers
     * Churn labels correctly identify inactive customers
     * Derived metrics handle nulls and edge cases properly
     * Log + scaling transformations produce standardized distributions
}
