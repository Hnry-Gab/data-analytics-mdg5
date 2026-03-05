"""
Configurações da aplicação FastAPI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
STATIC_DIR = SRC_DIR / "static"

# Configurações do modelo
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "xgboost_model.pkl"))
CSV_PATH = os.getenv("CSV_PATH", str(BASE_DIR / "data" / "olist_processed.csv"))

# Configurações da aplicação
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
