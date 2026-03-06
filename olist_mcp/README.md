# Olist Analytics MCP Server

MCP (Model Context Protocol) server that exposes 60 analytics tools for the Olist Brazilian E-Commerce dataset. Designed for integration with Claude Desktop and other MCP-compatible clients.

## Quick Start

### Prerequisites

- Python 3.11+
- Dataset file: `notebooks/final_analysis/dataset_unificado_v1.csv`

### Installation

```bash
pip install -r olist_mcp/requirements.txt
```

### Run the Server

```bash
python -m olist_mcp.server
```

The server uses **stdio transport** (no network configuration needed). It starts as a subprocess managed by the MCP client.

## Claude Desktop Integration

Add the following to your Claude Desktop configuration file:

**Linux:** `~/.config/Claude/claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "olist-analytics": {
      "command": "python",
      "args": ["-m", "olist_mcp.server"],
      "cwd": "/absolute/path/to/data-analytics-mdg5"
    }
  }
}
```

Replace `/absolute/path/to/data-analytics-mdg5` with the actual project root path. Restart Claude Desktop after saving.

## Claude Code Integration

Add to `.claude/settings.json` or use the CLI:

```json
{
  "mcpServers": {
    "olist-analytics": {
      "command": "python",
      "args": ["-m", "olist_mcp.server"],
      "cwd": "/absolute/path/to/data-analytics-mdg5"
    }
  }
}
```

## Tools (60 total)

### Category 1: Dataset Statistics (6 tools)

| Tool | Description |
|------|-------------|
| `get_dataset_overview` | Shape, columns, dtypes, memory usage |
| `get_column_statistics` | Descriptive stats for a specific column |
| `get_class_distribution` | Target variable (foi_atraso) distribution |
| `get_correlation_table` | Pearson/Cramér's V correlation ranking |
| `get_dataset_schema` | Full schema with dtypes and null counts |
| `get_training_dataset_info` | Training dataset details |

### Category 2: Geographic Analysis (8 tools)

| Tool | Description |
|------|-------------|
| `get_delay_rate_by_customer_state` | Delay rates by customer state |
| `get_delay_rate_by_seller_state` | Delay rates by seller state |
| `get_interstate_vs_intrastate_analysis` | Interstate vs intrastate comparison |
| `get_route_heatmap_data` | Raw heatmap data for state routes |
| `get_macro_region_analysis` | Analysis by macro-region |
| `get_distance_analysis` | Haversine distance vs delay correlation |
| `get_worst_routes` | Routes with highest delay rates |
| `calculate_haversine_distance` | Calculate distance between two coordinates |

### Category 3: ML Model & Prediction (7 tools)

| Tool | Description |
|------|-------------|
| `get_model_status` | Model availability and configuration |
| `predict_delay_probability` | Predict delay for a single order |
| `get_model_metrics` | Baseline ROC-AUC, Recall, F1 targets |
| `get_feature_importance` | Feature ranking (model or correlation proxy) |
| `get_model_hyperparameters` | XGBoost hyperparameters |
| `get_state_encoding_map` | Target-encoded state values |
| `simulate_seller_improvement` | Simulate dispatch speed improvements |

All ML tools degrade gracefully when the model file (`models/xgboost_atraso_v1.pkl`) is absent, returning alternative tools and spec-defined baselines.

### Category 4: Business Insights (7 tools)

| Tool | Description |
|------|-------------|
| `get_top_worst_sellers` | Sellers with highest delay rates |
| `get_top_worst_categories` | Product categories with highest delays |
| `get_business_summary` | Executive summary of all findings |
| `get_growth_recommendations` | Actionable business recommendations |
| `get_seller_profile` | Detailed profile for a specific seller |
| `get_national_delay_rate` | National delay rate overview |
| `get_price_freight_analysis` | Price and freight vs delay correlation |

### Category 5: Temporal Analysis (6 tools)

| Tool | Description |
|------|-------------|
| `get_delay_rate_by_month` | Monthly delay rate patterns |
| `get_delay_rate_by_weekday` | Day-of-week analysis |
| `get_orders_over_time` | Order volume time series |
| `get_date_range` | Dataset date coverage |
| `get_velocidade_lojista_distribution` | Seller dispatch speed analysis |
| `get_seasonal_analysis` | Quarterly seasonal patterns |

### Category 6: Documentation (11 tools)

| Tool | Description |
|------|-------------|
| `get_column_definition` | Definition of a specific column |
| `get_data_dictionary` | Full data dictionary |
| `get_project_spec` | Project specification document |
| `get_model_spec` | ML model specification |
| `get_feature_engineering_plan` | Feature engineering methodology |
| `get_viability_report` | Target encoding viability analysis |
| `get_eda_report` | EDA findings summary |
| `get_task_details` | Details of a specific pipeline task |
| `list_all_tasks` | All pipeline tasks overview |
| `get_algorithm_explanation` | Algorithm explanations (XGBoost, etc.) |
| `get_stack_info` | Technology stack information |

### Category 7: Visualization (7 tools)

| Tool | Description |
|------|-------------|
| `list_available_charts` | Inventory of all available charts |
| `get_chart_as_base64` | Get pre-built chart as base64 PNG |
| `get_html_chart_content` | Get interactive Plotly HTML chart |
| `generate_delay_by_state_chart` | Generate live state delay chart |
| `generate_correlation_bar_chart` | Generate live correlation chart |
| `generate_route_heatmap` | Generate live route heatmap |
| `generate_time_series_chart` | Generate live time series chart |

### Category 8: Query & Filter (8 tools)

| Tool | Description |
|------|-------------|
| `filter_orders` | Composite filter with aggregate stats |
| `get_orders_by_state_pair` | Route-specific analysis |
| `get_category_deep_dive` | Deep analysis of a product category |
| `search_orders_by_order_id` | Look up a specific order |
| `get_product_weight_analysis` | Weight vs delay analysis |
| `compare_two_states` | Side-by-side state comparison |
| `get_high_risk_order_profile` | Profile of a typical delayed order |
| `get_seller_ranking` | Seller rankings by various metrics |

## Architecture

```
olist_mcp/
├── __init__.py          # Package version
├── server.py            # FastMCP server entry point
├── config.py            # Paths, dtypes, column lists
├── cache.py             # DataStore singleton (lazy-loading, thread-safe)
├── requirements.txt     # Dependencies
├── tools/
│   ├── dataset_stats.py     # 6 tools
│   ├── geographic.py        # 8 tools
│   ├── ml_model.py          # 7 tools (graceful degradation)
│   ├── business_insights.py # 7 tools
│   ├── temporal.py          # 6 tools
│   ├── documentation.py     # 11 tools
│   ├── visualization.py     # 7 tools (Plotly + Kaleido)
│   └── query_filter.py      # 8 tools
└── utils/
    ├── formatters.py        # Markdown table formatting
    ├── state_mappings.py    # State → region mappings
    └── haversine.py         # Distance calculations
```

## Performance

- **First call:** ~800ms (dataset loading + caching)
- **Subsequent calls:** <500ms (all data/analytics tools)
- **Chart generation:** <3000ms (Plotly + Kaleido rendering)
- **Dataset:** 110,189 rows x 41 columns (~55 MB)

## Testing

```bash
# Run all tests (298 tests)
python -m pytest tests/test_mcp_*.py -v

# Run by category
python -m pytest tests/test_mcp_integration.py     # 57 integration tests
python -m pytest tests/test_mcp_performance.py      # 52 performance tests
python -m pytest tests/test_mcp_error_handling.py   # 26 error handling tests
python -m pytest tests/test_mcp_foundation.py       # 26 foundation tests
python -m pytest tests/test_mcp_dataset_stats.py    # 16 dataset tests
python -m pytest tests/test_mcp_documentation.py    # 21 documentation tests
python -m pytest tests/test_mcp_geographic.py       # 16 geographic tests
python -m pytest tests/test_mcp_temporal.py         # 13 temporal tests
python -m pytest tests/test_mcp_business_insights.py # 13 business tests
python -m pytest tests/test_mcp_ml_model.py         # 11 ML model tests
python -m pytest tests/test_mcp_query_filter.py     # 26 query/filter tests
python -m pytest tests/test_mcp_visualization.py    # 21 visualization tests
```

## Key Data Points

| Metric | Value |
|--------|-------|
| National delay rate | 6.77% |
| Highest state (customer) | AL = 20.84% |
| Interstate delay rate | ~8% |
| Intrastate delay rate | ~4.5% |
| Strongest feature | velocidade_lojista_dias (r = +0.2143) |
| XGBoost baseline ROC-AUC | 0.7452 |
