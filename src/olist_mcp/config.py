"""Configuration: paths, dtype mappings, and constants."""

from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = ROOT / "src"
DOCS_DIR = ROOT / "docs"

DATASET_V1 = SRC_ROOT / "notebooks" / "dataset_unificado_v1.csv"
CATBOOST_MODEL = SRC_ROOT / "models" / "catboost_atraso_v5.cbm"
CATBOOST_CONFIG = SRC_ROOT / "models" / "model_config.json"
IMAGES_DIR = SRC_ROOT / "notebooks" / "images"
HTML_DIR = SRC_ROOT / "notebooks"
RAW_DATA_DIR = SRC_ROOT / "dataset"

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
