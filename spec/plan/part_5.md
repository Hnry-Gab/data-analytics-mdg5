# PART 5: Churn Prediction

## Micro-Plan Objective
Develop a robust churn prediction model using XGBoost to identify at-risk customers with high accuracy, enabling proactive retention strategies and targeted interventions.

---

## Dataframes Utilized + Schemas

### 1. Churn Training Features Dataframe
```python
df_churn_features = pd.DataFrame()
{
    'customer_unique_id': str,

    # RFM features (core predictors)
    'recency': float,               # Days since last purchase
    'frequency': int,                # Number of purchases
    'monetary': float,               # Total spend
    'recency_scaled': float,
    'frequency_scaled': float,
    'monetary_scaled': float,

    # Review features
    'avg_review_score': float,       # 1-5
    'review_count': int,
    'has_low_review': bool,          # True if any review <= 2
    'low_review_ratio': float,       # Count(reviews <= 2) / total_reviews

    # Delivery experience features
    'avg_delivery_delay_days': float,
    'has_late_delivery': bool,
    'late_delivery_rate': float,     # Count(delay > 0) / total_deliveries
    'avg_order_value': float,

    # Payment behavior
    'avg_payment_installments': float,
    'preferred_payment_type': str,    # One-hot encoded

    # Engagement features
    'days_between_purchases_avg': float,
    'days_between_purchases_std': float,
    'customer_age_days': float,

    # Geographic features
    'customer_state': str,           # One-hot encoded
    'customer_city': str,            # High-cardinality (might use target encoding)

    # Product category preferences
    'top_category': str,             # Most purchased category
    'category_diversity': float,     # Number of unique categories / total purchases

    # Target variable
    'is_churned': bool               # True if inactive > CHURN_THRESHOLD_DAYS
}
```

### 2. Churn Model Training Dataframe (One-hot encoded)
```python
df_churn_model = pd.DataFrame()
{
    # Numerical features (already in df_churn_features)
    # + One-hot encoded categorical features
    'payment_type_credit_card': int,
    'payment_type_boleto': int,
    'payment_type_voucher': int,
    'payment_type_debit_card': int,

    'state_SP': int,
    'state_RJ': int,
    'state_MG': int,
    # ... (one-hot for all 27 states)

    # Target
    'is_churned': int                # 0 or 1 (binary)
}
```

### 3. Churn Predictions Dataframe
```python
df_churn_predictions = pd.DataFrame()
{
    'customer_unique_id': str,
    'is_churned': bool,              # Actual churn label (training set)

    # Model predictions
    'churn_probability': float,      # XGBoost probability (0-1)
    'churn_prediction': bool,        # Binary prediction (threshold = 0.5)
    'churn_risk_level': str,         # 'Low', 'Medium', 'High'

    # RFM info for context
    'rfm_segment': str,
    'recency': float,
    'frequency': int,
    'monetary': float,

    # Review info
    'avg_review_score': float,
    'has_low_review': bool
}
```

### 4. Churn Model Evaluation Dataframe
```python
df_churn_evaluation = pd.DataFrame()
{
    'model': str,                    # 'XGBoost', 'RandomForest', 'LogisticRegression'
    'version': str,                  # 'baseline', 'v1', 'v2'

    # Metrics (on test set)
    'accuracy': float,
    'precision': float,
    'recall': float,
    'f1_score': float,
    'roc_auc': float,
    'pr_auc': float,                 # Precision-Recall AUC

    # Confusion matrix (test set)
    'tn': int,                       # True Negatives
    'fp': int,                       # False Positives
    'fn': int,                       # False Negatives
    'tp': int,                       # True Positives

    # Cross-validation
    'cv_roc_auc_mean': float,
    'cv_roc_auc_std': float
}
```

### 5. Churn Feature Importance Dataframe
```python
df_feature_importance = pd.DataFrame()
{
    'feature': str,
    'importance': float,
    'importance_pct': float,         # Percentage of total importance
    'importance_rank': int,          # 1 = most important

    # Feature metadata
    'feature_type': str             # 'numerical', 'categorical', 'derived'
}
```

### 6. Churn Risk Segment Summary Dataframe
```python
df_churn_segments = pd.DataFrame()
{
    'churn_risk_level': str,         # 'Low', 'Medium', 'High'
    'threshold': float,              # Probability threshold

    # Customer count
    'n_customers': int,
    'pct_customers': float,

    # Actual churn rate (if labeled)
    'actual_churn_rate': float,

    # Characteristics
    'avg_recency': float,
    'avg_frequency': float,
    'avg_monetary': float,
    'avg_review_score': float,

    # Business value
    'total_at_risk_clv': float,      # Total CLV at risk of churning
    'avg_clv_per_customer': float
}
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Implement churn feature engineering in models/churn.py
   - [ ] Create XGBoost model with hyperparameter tuning
   - [ ] Train churn model with train/test split and cross-validation
   - [ ] Generate churn predictions and risk levels (Low/Medium/High)
   - [ ] Calculate model evaluation metrics (ROC-AUC, Precision, Recall, F1)

   ## Medium Priority
   - [ ] Create feature importance analysis (XGBoost gain + SHAP values)
   - [ ] Implement churn segment summaries with business insights
   - [ ] Add baseline model comparison (RandomForest, LogisticRegression)
   - [ ] Create unit tests for churn model training and prediction
   - [ ] Build threshold analysis (optimize probability threshold for business KPI)

   ## Low Priority
   - [ ] Add early churn prediction (predict churn before 180 days)
   - [ ] Implement churn reason analysis (what drives churn per segment)

   ## Notes
   - Churn definition: is_churned = (recency_days > CHURN_THRESHOLD_DAYS)
     * CHURN_THRESHOLD_DAYS = 180 (no purchase in last 6 months)
     * ~96% of customers have only 1 purchase (high baseline churn)
   - Feature engineering:
     * RFM features are strongest predictors (recency especially)
     * Review features: avg_review_score, has_low_review, low_review_ratio
     * Delivery features: avg_delivery_delay_days, late_delivery_rate
     * Payment features: avg_installments, payment_type (one-hot encoded)
     * Geographic: customer_state (one-hot encoded, 27 states)
   - XGBoost model configuration:
     * objective: 'binary:logistic' (probability output)
     * eval_metric: 'auc' (primary metric), 'logloss', 'error'
     * scale_pos_weight: ratio of negative/positive samples (handle class imbalance)
     * max_depth: 6-8 (control overfitting)
     * learning_rate: 0.1-0.3
     * n_estimators: 100-500
     * subsample: 0.8-1.0
     * colsample_bytree: 0.8-1.0
     * random_state: 42 (reproducibility)
   - Hyperparameter tuning:
     * Use GridSearchCV or RandomizedSearchCV
     * 5-fold cross-validation
     * Optimize for ROC-AUC (handles class imbalance well)
   - Train/test split:
     * 80% training, 20% test (stratified by churn label)
     * Use train_test_split(stratify=is_churned)
   - Risk level thresholds:
     * Low Risk: churn_probability < 0.3
     * Medium Risk: 0.3 <= churn_probability < 0.7
     * High Risk: churn_probability >= 0.7
     * Thresholds can be optimized based on business cost (FP vs. FN trade-off)
   - Evaluation metrics:
     * Primary: ROC-AUC (handles class imbalance, threshold-independent)
     * Secondary: Precision, Recall, F1-score (for specific threshold)
     * PR-AUC: Precision-Recall AUC (better for highly imbalanced data)
   - Feature importance:
     * XGBoost built-in: gain, weight, cover, total_gain
     * SHAP values: Explain individual predictions (optional but recommended)
   - Baseline comparison:
     * RandomForest (similar ensemble approach)
     * LogisticRegression (simple baseline)
     * Compare ROC-AUC, F1-score, and feature importance
   - Edge cases:
     * Customers with no history: Use average imputation for missing features
     * Extreme outliers: Cap values at 99th percentile during feature engineering
     * High cardinality features (city): Drop or use target encoding
   - Unit tests must verify:
     * Churn label matches recency_days threshold
     * Model training completes without errors
     * Predictions are valid probabilities (0-1)
     * ROC-AUC is between 0.5 (random) and 1.0 (perfect)
     * Feature importance sums to 1.0
     * Risk level thresholds classify customers correctly
}
