# PART 3: Segmentation Models

## Micro-Plan Objective
Implement robust customer segmentation using K-Means RFM clustering and prepare data for probabilistic BG/NBD modeling, enabling actionable customer insights and targeted strategies.

---

## Dataframes Utilized + Schemas

### 1. RFM Cluster Assignments Dataframe
```python
df_rfm_clusters = pd.DataFrame()
{
    'customer_unique_id': str,
    'recency': float,
    'frequency': int,
    'monetary': float,

    # Transformed features
    'recency_scaled': float,
    'frequency_scaled': float,
    'monetary_scaled': float,

    # Cluster assignment
    'rfm_cluster': int,              # 0, 1, 2, 3, 4
    'rfm_segment': str,              # 'Champions', 'Loyal Customers', etc.

    # Cluster centroids (for reference)
    'cluster_recency_centroid': float,
    'cluster_frequency_centroid': float,
    'cluster_monetary_centroid': float
}
```

### 2. RFM Segment Summary Dataframe
```python
df_rfm_segment_summary = pd.DataFrame()
{
    'segment': str,                  # 5 unique segments
    'cluster_id': int,
    'n_customers': int,              # Count of customers in segment
    'pct_customers': float,         # Percentage of total customers
    'avg_recency': float,
    'avg_frequency': float,
    'avg_monetary': float,
    'total_gmv': float,              # Gross Merchandise Value
    'pct_gmv': float,                # Percentage of total GMV
    'avg_review_score': float,
    'churn_rate': float              # % of churned customers in segment
}
```

### 3. BG/NBD Data Preparation Dataframe
```python
df_bgnd_prep = pd.DataFrame()
{
    'customer_unique_id': str,

    # Frequency (number of repeat purchases)
    'frequency': int,                # Count of purchases - 1 (repeat purchases only)
    'recency': float,                # Time between first and last purchase (in days)
    'T': float,                      # Customer age (days between first purchase and reference date)
    'monetary_value': float          # Average monetary value of purchases
}
```

### 4. BG/NBD Model Parameters Dataframe
```python
df_bgnd_params = pd.DataFrame()
{
    'customer_unique_id': str,

    # Model parameters (fitted from BG/NBD)
    'predicted_purchases': float,    # Expected number of purchases in next period
    'alive_probability': float,      # Probability customer is still "alive" (0-1)

    # Gamma-Gamma parameters (monetary value)
    'expected_avg_monetary_value': float,

    # Combined predictions
    'clv_90_days': float,
    'clv_180_days': float,
    'clv_365_days': float
}
```

### 5. K-Means Model Metrics Dataframe
```python
df_kmeans_metrics = pd.DataFrame()
{
    'n_clusters': int,               # Tested: 2, 3, 4, 5, 6, 7, 8
    'inertia': float,                # Within-cluster sum of squares
    'silhouette_score': float,       # Average silhouette score
    'calinski_harabasz_score': float,
    'davies_bouldin_score': float,
    'is_selected': bool              # True if n_clusters = RFM_N_CLUSTERS (5)
}
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Implement K-Means RFM clustering in models/rfm.py
   - [ ] Create elbow method analysis for optimal cluster selection (test n_clusters: 2-8)
   - [ ] Calculate silhouette score and other clustering metrics
   - [ ] Develop segment labeling logic based on cluster centroids (Champions, Loyal, etc.)
   - [ ] Build BG/NBD data preparation pipeline (frequency, recency, T, monetary_value)
   - [ ] Implement segment summary statistics and insights generation

   ## Medium Priority
   - [ ] Create unit tests for clustering module (cluster stability, label assignment)
   - [ ] Add visualization preparation for RFM 3D scatter plot (R, F, M axes)
   - [ ] Implement segment-based customer profiling (avg review score, churn rate per segment)
   - [ ] Create cluster interpretation guide with business recommendations per segment

   ## Low Priority
   - [ ] Add alternative clustering algorithms (Agglomerative, DBSCAN) for comparison
   - [ ] Implement cluster stability analysis (re-run K-Means multiple times)

   ## Notes
   - K-Means clustering uses scaled features (recency_scaled, frequency_scaled, monetary_scaled)
   - Optimal clusters: n_clusters = 5 (determined by elbow method + silhouette score)
   - K-Means parameters: n_init=10, max_iter=300, random_state=42 (reproducibility)
   - Segment labeling rules:
     * Champions: High R (low recency), High F, High M
     * Loyal Customers: High R, Medium-High F, High M
     * Potential Loyalists: High R, Low F, Medium M
     * At Risk: Low R, Medium F, Medium-High M
     * Lost: Low R, Low F, Low M
   - BG/NBD data preparation requires specific lifetimes library format:
     * frequency: Number of repeat purchases (total orders - 1)
     * recency: Time between first and last purchase in days
     * T: Customer age (first purchase to reference date) in days
     * monetary_value: Average order value (for Gamma-Gamma)
   - Edge cases:
     * Single-purchase customers: frequency = 0 (no repeat purchases)
     * Same day purchases: recency = 0
     * Very recent customers: T may be small (less reliable predictions)
   - Unit tests must verify:
     * Cluster assignments are consistent for same inputs (random_state fixed)
     * Sum of customers across segments equals total customers
     * Segment labels match centroid-based rules
     * BG/NBD data format matches lifetimes library requirements
}
