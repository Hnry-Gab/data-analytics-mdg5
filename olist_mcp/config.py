"""Configuration: paths, dtype mappings, and constants."""

from pathlib import Path

ROOT = Path(__file__).parent.parent

DATASET_V1 = ROOT / "notebooks" / "final_analysis" / "log" / "dataset_unificado_v1.csv"
DATASET_TREINO = ROOT / "notebooks" / "final_analysis" / "dataset_treino_v1.csv"
CORRELATIONS_CSV = ROOT / "notebooks" / "final_analysis" / "tabela_resumo_correlacoes.csv"
MODEL_PKL = ROOT / "models" / "xgboost_atraso_v1.pkl"
IMAGES_DIR = ROOT / "notebooks" / "final_analysis" / "images"
HTML_DIR = ROOT / "notebooks" / "final_analysis"
DOCS_DIR = ROOT / "docs"
SPEC_DIR = ROOT / "spec"
RAW_DATA_DIR = ROOT / "dataset"

ZIP_DTYPE = {
    "customer_zip_code_prefix": str,
    "seller_zip_code_prefix": str,
}

TIMESTAMP_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
]
