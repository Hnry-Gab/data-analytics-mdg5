# PART 4: Value Prediction

## Micro-Plan Objective
Develop Customer Lifetime Value (CLV) prediction models using both simple heuristic formulas and advanced probabilistic BG/NBD + Gamma-Gamma modeling to identify high-value customers and optimize marketing investment.

---

## Dataframes Utilized + Schemas

### 1. Simple CLV Dataframe (Heuristic)
```python
df_clv_simple = pd.DataFrame()
{
    'customer_unique_id': str,

    # Input metrics
    'avg_order_value': float,
    'purchase_frequency': float,    # orders_per_year = order_count / customer_age_days * 365
    'customer_lifetime_days': float, # Time from first to last purchase

    # Simple CLV formula
    'clv_simple': float,            # CLV = avg_order_value * purchase_frequency * 365
    'clv_simple_90_days': float,    # Pro-rated to 90 days
    'clv_simple_180_days': float,   # Pro-rated to 180 days

    # Segment comparison
    'rfm_cluster': int,
    'rfm_segment': str
}
```

### 2. BG/NBD Fitted Model Parameters
```python
df_bgnd_fit = pd.DataFrame()
{
    # BG/NBD model parameters (fitted to dataset)
    'r': float,                      # Shape parameter for beta distribution
    'alpha': float,                  # Scale parameter for beta distribution
    'a': float,                      # Shape parameter for gamma distribution
    'b': float,                      # Scale parameter for gamma distribution

    # Gamma-Gamma model parameters
    'p': float,                      # Shape parameter for monetary value
    'q': float,                      # Shape parameter for monetary value
    'v': float,                      # Scale parameter for monetary value

    # Model fit statistics
    'aic': float,                    # Akaike Information Criterion
    'bic': float,                    # Bayesian Information Criterion
    'log_likelihood': float
}
```

### 3. BG/NBD Predictions Dataframe
```python
df_bgnd_predictions = pd.DataFrame()
{
    'customer_unique_id': str,

    # Input features (from BG/NBD prep)
    'frequency': int,                # Repeat purchases
    'recency': float,                # Time between first and last purchase
    'T': float,                      # Customer age in days
    'monetary_value': float,         # Average order value

    # Predictions: Number of future purchases
    'predicted_purchases_90_days': float,
    'predicted_purchases_180_days': float,
    'predicted_purchases_365_days': float,

    # Probabilities
    'alive_probability': float,      # Probability customer is still active (0-1)
    'churn_probability': float,     # 1 - alive_probability

    # Predictions: CLV (purchases * expected monetary value)
    'clv_bgnd_90_days': float,
    'clv_bgnd_180_days': float,
    'clv_bgnd_365_days': float
}
```

### 4. Combined CLV Comparison Dataframe
```python
df_clv_comparison = pd.DataFrame()
{
    'customer_unique_id': str,

    # Simple CLV
    'clv_simple_180_days': float,

    # BG/NBD CLV
    'clv_bgnd_180_days': float,

    # Comparison metrics
    'clv_diff': float,               # BG/NBD - Simple
    'clv_ratio': float,              # BG/NBD / Simple
    'clv_agreement': bool,           # True if within ±20% of each other

    # Rankings
    'clv_simple_rank': int,          # Rank by simple CLV (1 = highest)
    'clv_bgnd_rank': int,            # Rank by BG/NBD CLV (1 = highest)

    # Segment info
    'rfm_segment': str
}
```

### 5. CLV Segment Summary Dataframe
```python
df_clv_segments = pd.DataFrame()
{
    'segment': str,                  # 'High CLV', 'Medium CLV', 'Low CLV'
    'n_customers': int,
    'pct_customers': float,

    # CLV statistics (BG/NBD 180 days)
    'avg_clv': float,
    'median_clv': float,
    'total_clv': float,
    'pct_total_clv': float,

    # Segment characteristics
    'avg_recency': float,
    'avg_frequency': float,
    'avg_monetary': float,
    'avg_alive_probability': float,

    # Business insights
    'churn_rate': float,
    'avg_review_score': float
}
```

### 6. CLV Model Evaluation Dataframe
```python
df_clv_evaluation = pd.DataFrame()
{
    'model': str,                    # 'Simple CLV', 'BG/NBD CLV'
    'horizon': str,                  # '90 days', '180 days', '365 days'

    # Hold-out set performance (predict future 90 days from past data)
    'mae': float,                    # Mean Absolute Error
    'mape': float,                   # Mean Absolute Percentage Error
    'rmse': float,                   # Root Mean Squared Error
    'r2_score': float                # Coefficient of determination
}
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Implement simple CLV calculation in models/clv.py (formula: AOV * frequency * 365)
   - [ ] Develop BG/NBD model fitting with lifetimes library
   - [ ] Create Gamma-Gamma model for monetary value prediction
   - [ ] Build CLV prediction pipeline for 90/180/365 day horizons
   - [ ] Implement customer segmentation based on CLV quantiles (High/Medium/Low)

   ## Medium Priority
   - [ ] Add model evaluation with hold-out test set (predict future 90 days)
   - [ ] Create CLV comparison analysis (Simple vs. BG/NBD agreement/disagreement)
   - [ ] Generate CLV segment summaries with business insights
   - [ ] Implement unit tests for CLV calculations and predictions
   - [ ] Add visualization data preparation (CLV distribution, segment comparison)

   ## Low Priority
   - [ ] Add advanced CLV features (discount rate, profit margin consideration)
   - [ ] Implement CLV trend analysis over time

   ## Notes
   - Simple CLV formula: CLV = avg_order_value * purchase_frequency * 365
     * purchase_frequency = order_count / customer_age_days * 365
     * Works best for stable, recurring purchase patterns
   - BG/NBD model (Beta-Geometric/Negative Binomial Distribution):
     * Predicts number of future purchases based on past transaction history
     * Handles "dropout" (churn) behavior probabilistically
     * Parameters: r, alpha (purchase process), a, b (dropout process)
   - Gamma-Gamma model:
     * Predicts expected monetary value per transaction
     * Assumes monetary value varies independently of purchase process
     * Parameters: p, q, v
   - Lifetimes library workflow:
     1. Prepare data: frequency, recency, T, monetary_value
     2. Fit BG/NBD: BetaGeoFitter().fit(frequency, recency, T, monetary_value)
     3. Fit Gamma-Gamma: GammaGammaFitter().fit(frequency, recency, T, monetary_value)
     4. Predict: conditional_expected_number_of_purchases_up_to_time()
     5. Calculate CLV: customer_lifetime_value(gamma_gamma_model, bgf_model, frequency, recency, T, monetary_value, time=...)
   - Hold-out evaluation:
     * Split data: First 80% of timeline for training, last 20% for testing
     * Compare predicted vs. actual purchases in test period
     * Metrics: MAE, MAPE, RMSE, R²
   - CLV segmentation (based on BG/NBD 180-day CLV):
     * High CLV: Top 25% of customers
     * Medium CLV: 25th-75th percentile
     * Low CLV: Bottom 25% of customers
   - Edge cases:
     * Single-purchase customers: frequency = 0 (BG/NBD handles this)
     * Negative CLV predictions: Clip to 0 (can occur in probabilistic models)
     * Very recent customers: Predictions may be less reliable (short observation period)
   - Unit tests must verify:
     * Simple CLV formula matches manual calculation for sample customers
     * BG/NBD model converges (no runtime errors)
     * CLV predictions are non-negative
     * Segment quantiles divide customers correctly
     * Model evaluation metrics are calculated correctly
}
