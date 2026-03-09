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
# O Frontend real da aplicação está na raiz do projeto (frontend/) e não em src/static
STATIC_DIR = BASE_DIR / "frontend"

# Configurações do modelo
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "catboost_atraso_v5.cbm"))
MODEL_CONFIG_PATH = os.getenv("MODEL_CONFIG_PATH", str(BASE_DIR / "models" / "model_config.json"))
CSV_PATH = os.getenv("CSV_PATH", str(BASE_DIR / "dataset"))

# Configurações da aplicação
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
