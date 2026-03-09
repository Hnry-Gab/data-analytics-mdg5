"""Configuration: paths, dtype mappings, and constants."""

from pathlib import Path

ROOT = Path(__file__).parent.parent

DATASET_V1 = ROOT / "notebooks" / "individual" / "Lucas" / "dataset_unificado_v1.csv"
CATBOOST_MODEL = ROOT / "models" / "v5" / "catboost_atraso_v5.cbm"
CATBOOST_CONFIG = ROOT / "models" / "v5" / "model_config.json"
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
