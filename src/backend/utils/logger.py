"""
Configuração de logging para a aplicação
"""
import logging
import sys
from pathlib import Path
from backend.config import LOG_LEVEL

# Criar diretório de logs se não existir
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configurar formato dos logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Cria e configura um logger com handlers para console e arquivo

    Args:
        name: Nome do logger (geralmente __name__ do módulo)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Evitar duplicação de handlers
    if logger.handlers:
        return logger

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)

    # Handler para arquivo
    file_handler = logging.FileHandler(LOG_DIR / "app.log")
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Adicionar handlers ao logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
