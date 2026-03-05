# PART 6: Advanced Analytics

## Micro-Plan Objective
Implement advanced analytics including NLP sentiment analysis on reviews, market basket analysis for cross-sell recommendations, and uplift modeling for causal inference to drive targeted marketing interventions.

---

## Dataframes Utilized + Schemas

### 1. NLP Preprocessed Reviews Dataframe
```python
df_reviews_nlp = pd.DataFrame()
{
    'review_id': str,
    'order_id': str,
    'customer_unique_id': str,

    # Original text
    'review_comment_title': str,
    'review_comment_message': str,
    'combined_text': str,           # title + message

    # Preprocessing
    'text_lowercase': str,
    'text_no_stopwords': str,
    'text_tokenized': list,         # List of tokens
    'text_stemmed': list,           # List of stemmed tokens
    'text_lemmatized': list,        # List of lemmatized tokens

    # Features
    'word_count': int,
    'char_count': int,
    'avg_word_length': float,
    'has_mentions': bool,
    'has_numbers': bool,

    # Ground truth
    'review_score': int,             # 1-5 (for sentiment labeling)
    'review_date': datetime
}
```

### 2. Sentiment Analysis Results Dataframe
```python
df_sentiment = pd.DataFrame()
{
    'review_id': str,
    'order_id': str,
    'customer_unique_id': str,

    # Ground truth (derived from review_score)
    'review_score': int,
    'true_sentiment': str,          # 'positive', 'neutral', 'negative'
    'true_sentiment_score': int,    # -1 (negative), 0 (neutral), +1 (positive)

    # Model predictions
    'predicted_sentiment': str,      # 'positive', 'neutral', 'negative'
    'sentiment_probability': float,  # Confidence score (0-1)
    'predicted_sentiment_score': float, # -1 to +1

    # Model evaluation (if labeled)
    'is_correct': bool,             # True if prediction matches ground truth

    # TF-IDF features (top 20 words by importance)
    'tfidf_top_words': list,        # List of (word, score) tuples

    # Keywords extracted (NLP analysis)
    'keywords_positive': list,       # Positive sentiment keywords
    'keywords_negative': list,       # Negative sentiment keywords

    # Customer aggregation (for RFM correlation)
    'recency': float,
    'rfm_segment': str
}
```

### 3. Sentiment Model Evaluation Dataframe
```python
df_sentiment_eval = pd.DataFrame()
{
    'model': str,                   # 'LogisticRegression', 'NaiveBayes', 'SVM'
    'vectorizer': str,              # 'TF-IDF', 'Count', 'TF'

    # Test set performance
    'accuracy': float,
    'precision_macro': float,
    'recall_macro': float,
    'f1_macro': float,
    'confusion_matrix': dict,       # 3x3 matrix (positive/neutral/negative)

    # Per-class metrics
    'precision_positive': float,
    'recall_positive': float,
    'f1_positive': float,

    'precision_neutral': float,
    'recall_neutral': float,
    'f1_neutral': float,

    'precision_negative': float,
    'recall_negative': float,
    'f1_negative': float
}
```

### 4. Market Basket Analysis Dataframe
```python
df_basket = pd.DataFrame()
{
    'order_id': str,
    'product_id': str,
    'product_category_name_english': str,
    'price': float,
    'quantity': int,                # Always 1 in this dataset (one row per item)
    'is_purchased': int             # 1 (for Apriori algorithm)
}
```

### 5. Frequent Itemsets Dataframe (Apriori)
```python
df_frequent_itemsets = pd.DataFrame()
{
    'itemset': frozenset,           # Set of product categories or product_ids
    'itemset_str': str,             # String representation for display
    'n_items': int,                 # Size of itemset (1, 2, 3, ...)
    'support': float,               # Support count / total_transactions
    'n_transactions': int          # Number of transactions containing itemset
}
```

### 6. Association Rules Dataframe
```python
df_association_rules = pd.DataFrame()
{
    'antecedents': frozenset,        # If {antecedents} then {consequents}
    'consequents': frozenset,
    'antecedents_str': str,
    'consequents_str': str,

    # Rule metrics
    'support': float,               # P(A and B) / total_transactions
    'confidence': float,            # P(B | A) = support(A ∪ B) / support(A)
    'lift': float,                  # P(B | A) / P(B)
    'conviction': float,            # Expected dependency (1 if independent)
    'leverage': float,              # P(A ∪ B) - P(A) * P(B)

    # Rule metadata
    'n_antecedents': int,
    'n_consequents': int,
    'is_significant': bool          # True if lift > 1.0 (better than random)
}
```

### 7. Cross-Sell Recommendations Dataframe
```python
df_cross_sell = pd.DataFrame()
{
    'customer_unique_id': str,
    'current_basket': list,          # Categories in customer's typical purchases
    'recommended_category': str,     # Category to recommend
    'recommendation_score': float,   # Confidence or lift score

    # Rule details
    'rule_antecedents': list,
    'rule_consequents': list,
    'rule_confidence': float,
    'rule_lift': float,

    # Customer context
    'recency': float,
    'frequency': int,
    'monetary': float,
    'rfm_segment': str,

    # Expected impact
    'expected_clv_impact': float,    # Estimated CLV increase from cross-sell
    'purchase_probability': float    # Probability of accepting recommendation
}
```

### 8. Uplift Modeling Dataframe
```python
df_uplift = pd.DataFrame()
{
    'customer_unique_id': str,

    # Treatment assignment (synthetic/observed)
    'treatment': bool,              # True if received intervention (marketing campaign)
    'outcome': bool,                # True if made purchase after intervention

    # Customer features (for modeling)
    'recency': float,
    'frequency': int,
    'monetary': float,
    'avg_review_score': float,
    'has_low_review': bool,
    'avg_delivery_delay_days': float,
    'rfm_segment': str,

    # Uplift predictions
    'uplift_score': float,          # Predicted causal effect (0-1)
    'control_outcome_prob': float,  # Probability of purchase without treatment
    'treatment_outcome_prob': float, # Probability of purchase with treatment

    # Segmentation for targeting
    'uplift_segment': str,         # 'Persuadables', 'Sure Things', 'Lost Causes', 'Sleeping Dogs'

    # Business metrics
    'expected_gain': float          # Expected revenue uplift from targeting
}
```

### 9. Uplift Model Evaluation Dataframe
```python
df_uplift_eval = pd.DataFrame()
{
    'model': str,                   # 'TwoModel', 'IPW', 'T-Learner', 'X-Learner', 'R-Learner'
    'version': str,

    # Uplift metrics
    'auuc': float,                  # Area Under Uplift Curve
    'qini_auc': float,              # Qini coefficient AUC

    # Targeting efficiency
    'top_10_percent_uplift': float, # Uplift in top 10% by uplift score
    'top_20_percent_uplift': float, # Uplift in top 20% by uplift score
    'top_30_percent_uplift': float,

    # Baseline comparison
    'random_uplift': float,         # Average uplift for random targeting
    'all_uplift': float             # Average uplift for targeting everyone
}
```

### 10. Topic Modeling Dataframe (Optional)
```python
df_topics = pd.DataFrame()
{
    'review_id': str,
    'order_id': str,
    'customer_unique_id': str,

    # Topic distribution per review
    'dominant_topic': int,          # 0, 1, 2, ... (topic number)
    'dominant_topic_prob': float,   # Probability of dominant topic (0-1)
    'topic_distribution': dict,     # {topic_id: probability} for all topics

    # Top words in dominant topic
    'top_words': list,              # List of top 5-10 words in topic
    'top_words_scores': list        # Word importance scores
}
```

---

## Tasks (RALPH Structure)

RALPH {
   ## High Priority
   - [ ] Implement NLP preprocessing pipeline in models/sentiment.py (lowercase, stopwords, tokenization, stemming)
   - [ ] Create TF-IDF vectorization for review comments
   - [ ] Train sentiment classification model (LogisticRegression or NaiveBayes)
   - [ ] Implement market basket analysis with Apriori algorithm in models/cross_sell.py
   - [ ] Generate association rules with metrics (support, confidence, lift)
   - [ ] Create cross-sell recommendations for customers

   ## Medium Priority
   - [ ] Implement uplift modeling with CausalML (Two-Model or T-Learner)
   - [ ] Create uplift segment definitions (Persuadables, Sure Things, Lost Causes, Sleeping Dogs)
   - [ ] Add sentiment model evaluation with classification report
   - [ ] Generate cross-sell recommendations by customer segment
   - [ ] Create unit tests for NLP, cross-sell, and uplift modules

   ## Low Priority
   - [ ] Add topic modeling (LDA) for discovering review themes
   - [ ] Implement SHAP explanations for uplift model
   - [ ] Add advanced NLP features (named entities, part-of-speech tagging)

   ## Notes
   - NLP Preprocessing (Portuguese):
     * Lowercase conversion: str.lower()
     * Stopword removal: nltk.corpus.stopwords.words('portuguese')
     * Tokenization: nltk.word_tokenize()
     * Stemming: nltk.stem.SnowballStemmer('portuguese')
     * Remove punctuation, numbers, extra whitespace
   - Sentiment labeling (ground truth):
     * Derive from review_score: positive (4-5), neutral (3), negative (1-2)
     * Use as supervised labels for classification
   - TF-IDF Vectorization:
     * Use TfidfVectorizer from sklearn
     * max_features: 5000-10000 (limit vocabulary size)
     * ngram_range: (1, 2) (unigrams + bigrams)
     * min_df: 5 (ignore words appearing in <5 docs)
     * max_df: 0.95 (ignore words appearing in >95% of docs)
   - Sentiment models:
     * LogisticRegression: Simple, interpretable, fast
     * MultinomialNB: Good for text classification
     * SVM: High accuracy but slower
     * Primary metric: F1-score macro average (handles class imbalance)
   - Market Basket Analysis:
     * Use mlxtend library (apriori, association_rules)
     * Group by order_id, collect product categories
     * Convert to one-hot encoded transaction matrix
     * min_support: 0.01 (1% of transactions)
     * Apriori parameters: max_len=3 (itemsets up to 3 items)
   - Association Rules:
     * metric='confidence', min_threshold=0.3
     * Key metrics:
       * Support: P(A ∪ B) (how frequent the rule is)
       * Confidence: P(B | A) (how often B occurs when A occurs)
       * Lift: P(B | A) / P(B) (>1 means A and B occur together more than expected)
       * Conviction: Dependency strength (1 if independent)
   - Cross-sell recommendations:
     * For each customer, find rules where their purchased categories match antecedents
     * Recommend consequents with highest confidence or lift
     * Filter rules by segment (e.g., only recommend high-margin products to high-value customers)
   - Uplift Modeling (Causal Inference):
     * Problem: Identify customers who respond positively to treatment
     * Segments:
       - Persuadables: Buy only if treated (positive uplift)
       - Sure Things: Buy regardless of treatment (zero uplift, no treatment needed)
       - Lost Causes: Won't buy regardless of treatment (zero uplift, waste of resources)
       - Sleeping Dogs: Buy without treatment, but not with treatment (negative uplift, avoid treatment)
     * Models:
       - Two-Model: Separate models for treatment and control, subtract predictions
       - T-Learner: Same as Two-Model, uses XGBoost or LightGBM
       - CausalML Meta-Learners: R-Learner, X-Learner, IPW
     * Evaluation: AUUC (Area Under Uplift Curve), Qini coefficient
   - Edge cases:
     * Empty review comments: Skip sentiment analysis, mark as 'no_text'
     * Single-item orders: Skip market basket analysis (can't form rules)
     * No treatment data: Create synthetic treatment or use proxy (e.g., high-value customers)
   - Unit tests must verify:
     * NLP preprocessing produces valid tokens (no empty strings)
     * Sentiment model predicts one of three classes
     * TF-IDF features are sparse matrices with correct shape
     * Apriori finds frequent itemsets (support > min_support)
     * Association rules have lift >= 1.0 (filter negative correlations)
     * Cross-sell recommendations match customer purchase history
     * Uplift scores are within reasonable range (-1 to +1)
     * Uplift segments cover all possible outcomes
}
