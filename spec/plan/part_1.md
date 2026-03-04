# PART 1: Data Pipeline Foundation

## Micro-Plan Objective
Establish a robust data pipeline foundation with efficient data ingestion, comprehensive cleaning, and modular caching infrastructure to support all downstream analytics and modeling.

---

## Dataframes Utilized + Schemas

### 1. Raw Dataframes (from CSVs)
```python
# Raw tables loaded from test_template/data/raw/*.csv
df_customers = pd.DataFrame()      # 99,442 rows
df_orders = pd.DataFrame()         # 99,442 rows
df_order_items = pd.DataFrame()    # 112,651 rows
df_payments = pd.DataFrame()       # 103,887 rows
df_reviews = pd.DataFrame()        # 104,720 rows
df_products = pd.DataFrame()       # 32,952 rows
df_sellers = pd.DataFrame()        # 3,096 rows
df_category_translation = pd.DataFrame()  # 71 rows
```

### 2. Master Order Dataframe (after joins)
```python
df_master_orders = pd.DataFrame()
# Schema: Combined from all tables
# Primary join keys:
# - customers.customer_id = orders.customer_id
# - orders.order_id = order_items.order_id
# - orders.order_id = payments.order_id
# - orders.order_id = reviews.order_id
# - order_items.product_id = products.product_id
# - order_items.seller_id = sellers.seller_id
# - products.product_category_name = category_translation.product_category_name
```

### 3. Configuration Module
```python
# src/config.py
CSV_FILES = {
    'customers': 'data/raw/olist_customers_dataset.csv',
    'orders': 'data/raw/olist_orders_dataset.csv',
    'order_items': 'data/raw/olist_order_items_dataset.csv',
    'payments': 'data/raw/olist_order_payments_dataset.csv',
    'reviews': 'data/raw/olist_order_reviews_dataset.csv',
    'products': 'data/raw/olist_products_dataset.csv',
    'sellers': 'data/raw/olist_sellers_dataset.csv',
    'category_translation': 'data/raw/product_category_name_translation.csv'
}
CACHE_DIR = 'data/processed/'
REFERENCE_DATE = '2018-10-17'
CHURN_THRESHOLD_DAYS = 180
RFM_N_CLUSTERS = 5
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Create project directory structure and configuration module
   - [ ] Implement data_loader.py with CSV ingestion and master order join
   - [ ] Develop data_cleaner.py with comprehensive cleaning pipeline
   - [ ] Build cache.py module with parquet serialization and decorators

   ## Medium Priority
   - [ ] Implement unit tests for data_loader, data_cleaner, and cache modules
   - [ ] Create data validation and quality checks with reporting

   ## Low Priority
   - [ ] Add performance profiling and optimization for data loading

   ## Notes
   - All CSV files should be moved from test_template/data/raw/ to data/raw/ first
   - Master order join must be done sequentially to avoid data loss: orders → customers → order_items → payments → reviews → products → sellers → category_translation
   - Use parquet with snappy compression for caching (read/write faster than CSV)
   - @cache_dataframe decorator should handle both saving and loading automatically
   - Data cleaning must handle: null values in delivery dates, timestamp parsing (multiple formats), outliers (cap at 99th percentile)
   - Unit tests should cover: schema validation, join correctness, null handling, cache hit/miss scenarios
}
