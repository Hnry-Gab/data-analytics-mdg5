# Olist Analytics MCP Server

MCP (Model Context Protocol) server that exposes 22 analytics tools for the Olist Brazilian E-Commerce dataset. Designed for integration with Claude Desktop and other MCP-compatible clients.

**Latest refactor (v0.2.0):** 60 → 22 tools, XGBoost → CatBoost V5, 8 → 5 categories.

## Quick Start

### Prerequisites

- Python 3.11+
- Dataset file: `notebooks/individual/Lucas/dataset_unificado_v1.csv`
- Model file: `models/v5/catboost_atraso_v5.cbm`

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

## Tools (22 total)

### Category 1: Dataset Statistics (5 tools)

| Tool | Description |
|------|-------------|
| `get_dataset_overview` | Shape, columns, dtypes, memory usage, target distribution |
| `get_column_statistics` | Descriptive stats for a specific column |
| `get_dataset_schema` | Full schema with dtypes and descriptions (33 direct + 25 engineered) |
| `search_orders_by_order_id` | Look up a specific order by ID |
| `calculate_haversine_distance_tool` | Calculate distance between two coordinates |

### Category 2: Dynamic Query (4 tools)

| Tool | Description |
|------|-------------|
| `dynamic_aggregate` | Aggregate any column with optional filters (mean, sum, count, min, max, median, std, nunique, value_counts) |
| `group_by_metrics` | Group by column + compute multiple metrics with sort/limit |
| `top_n_query` | Get top/bottom N rows sorted by a column, with optional aggregation |
| `compare_groups` | Compare two groups side-by-side on multiple metrics |

**Filter format:** `[{"column": "customer_state", "op": "eq", "value": "SP"}]`

**Supported operators:** `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `contains`, `in`, `notnull`

### Category 3: CatBoost ML (4 tools)

| Tool | Description |
|------|-------------|
| `predict_delay_catboost` | Predict delay probability for a single order (19 features, derived internally) |
| `get_catboost_model_info` | Full model metrics, hyperparameters, features, SMOTE config |
| `get_catboost_feature_importance` | Ranked feature importance (fallback: Pearson correlation) |
| `simulate_scenario` | Simulate varying one feature's effect on delay probability |

**Model specs:**
- Framework: CatBoost V5
- Features: 19 (automatically derived from raw data)
- Threshold: 0.54
- ROC-AUC: 0.8454
- Training: SMOTE with stratified 80/20 split

### Category 4: Business Insights (2 tools)

| Tool | Description |
|------|-------------|
| `get_business_summary` | Executive summary: 5 key findings with recommendations |
| `get_seller_profile` | Detailed seller profile: delay rate, ranking, dispatch speed |

### Category 5: Visualization (7 tools)

| Tool | Description |
|------|-------------|
| `list_available_charts` | Inventory of static PNG + interactive HTML + live charts |
| `get_chart_as_base64` | Get pre-built EDA chart as base64 PNG |
| `get_html_chart_content` | Get interactive Plotly HTML chart content |
| `generate_delay_by_state_chart` | Live bar chart of delay rate by state |
| `generate_correlation_bar_chart` | Live correlation chart with foi_atraso |
| `generate_route_heatmap` | Live seller×customer delay rate heatmap |
| `generate_time_series_chart` | Live dual-axis time series (orders + delay rate) |

## Architecture

```
olist_mcp/
├── __init__.py          # Package version (0.2.0)
├── server.py            # FastMCP server entry point (5 module registrations)
├── config.py            # Paths, dtypes, column lists
├── cache.py             # DataStore singleton (lazy-loading, thread-safe, CatBoost loader)
├── requirements.txt     # Dependencies
├── tools/
│   ├── dataset_stats.py     # 5 tools
│   ├── dynamic_query.py     # 4 tools (filter engine with 9 operators)
│   ├── catboost_ml.py       # 4 tools (feature derivation + prediction)
│   ├── business_insights.py # 2 tools
│   └── visualization.py     # 7 tools (Plotly + Kaleido)
└── utils/
    ├── formatters.py        # Markdown table formatting
    ├── state_mappings.py    # State → region mappings
    └── haversine.py         # Distance calculations
```

## Performance

- **First call:** ~800ms (dataset loading + caching)
- **Subsequent calls:** <500ms (all data/analytics tools)
- **Chart generation:** <3000ms (Plotly + Kaleido rendering)
- **Dataset:** 109,637 rows × 58 columns (~75 MB in memory)

## Testing

```bash
# Run all tests (~165 tests)
python -m pytest tests/test_mcp_*.py -v

# Run by category
python -m pytest tests/test_mcp_foundation.py       # Foundation tests
python -m pytest tests/test_mcp_dataset_stats.py    # Dataset stats tests
python -m pytest tests/test_mcp_dynamic_query.py    # Dynamic query tests
python -m pytest tests/test_mcp_catboost_ml.py      # CatBoost ML tests
python -m pytest tests/test_mcp_business_insights.py # Business insights tests
python -m pytest tests/test_mcp_visualization.py    # Visualization tests
python -m pytest tests/test_mcp_integration.py      # Integration tests
python -m pytest tests/test_mcp_error_handling.py   # Error handling tests
python -m pytest tests/test_mcp_performance.py      # Performance tests
python -m pytest tests/test_mcp_e2e.py              # End-to-end tests
```

## Key Data Points

| Metric | Value |
|--------|-------|
| National delay rate | 6.77% (6,535 / 96,439) |
| Highest state (customer) | AL = 20.84% |
| Second highest state | MA = 18.00% |
| Third highest state | SE = 16.27% |
| Interstate delay rate | ~8% |
| Intrastate delay rate | ~4.5% |
| Strongest feature | velocidade_lojista_dias (r = +0.2143) |
| CatBoost V5 ROC-AUC | 0.8454 |
| Model threshold | 0.54 |

## Dependencies

All dependencies are listed in `requirements.txt`:
- `fastmcp` — MCP protocol implementation
- `pandas` — Data manipulation
- `numpy` — Numerical computing
- `scikit-learn` — ML utilities (SMOTE, train_test_split)
- `catboost` — Gradient boosting (V5+)
- `plotly` — Interactive visualizations
- `Pillow` — Image processing
- `python-dateutil` — Date utilities
- `kaleido` — Static chart export
- `tabulate` — Markdown table formatting

## Troubleshooting

### Model file not found
If `models/v5/catboost_atraso_v5.cbm` is missing, all CatBoost tools will return graceful degradation messages with alternative insights.

### Dataset not found
If `notebooks/individual/Lucas/dataset_unificado_v1.csv` is missing, the server will fail to start. Ensure the dataset path is correct relative to the project root.

### Performance issues
- First call loads ~75 MB into memory (~800ms). Subsequent calls are fast.
- Chart generation with Kaleido can be slow on systems with limited CPU/memory. Consider using `get_html_chart_content` instead of PNG export for interactive use.

## Version History

- **v0.2.0** (current): Refactored to 22 tools, 5 categories, CatBoost V5
- **v0.1.0**: Original 60-tool architecture with XGBoost
