"""
Aplicação FastAPI principal - Olist Logistics API
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

from src.config import (
    STATIC_DIR,
    ALLOWED_ORIGINS,
    DEBUG,
    HOST,
    PORT
)
from src.api.routes import router as api_router
from src.chatbot.routes import router as chatbot_router
from src.core.ml_model import ml_model
from src.core.data_loader import data_loader
from src.utils.logger import get_logger
from src.utils.exceptions import OlistAPIException

logger = get_logger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Olist Logistics API",
    description="API para predição de atrasos logísticos no e-commerce Olist",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API
app.include_router(api_router)
app.include_router(chatbot_router)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Executado na inicialização da aplicação
    Carrega modelo e dados em memória
    """
    logger.info("=" * 60)
    logger.info("Iniciando Olist Logistics API")
    logger.info("=" * 60)

    # Carregar modelo ML
    try:
        ml_model.load_model()
        logger.info("✓ Modelo CatBoost V5 carregado com sucesso")
    except FileNotFoundError:
        logger.warning(
            "✗ Modelo não encontrado. API funcionará sem predições. "
            "Por favor, treine o modelo e salve em 'models/xgboost_model.pkl'"
        )
    except Exception as e:
        logger.error(f"✗ Erro ao carregar modelo: {str(e)}")

    # Carregar dados históricos (opcional)
    try:
        data_loader.load_csv()
        logger.info("✓ Dados históricos carregados com sucesso")
    except Exception as e:
        logger.warning(f"✗ Dados históricos não carregados: {str(e)}")

    # Carregar geolocalização (opcional)
    try:
        data_loader.load_geolocation()
        logger.info("✓ Geolocalização carregada com sucesso")
    except Exception as e:
        logger.warning(f"✗ Geolocalização não carregada: {str(e)}")

    # Iniciar chatbot MCP (opcional)
    from src.chatbot.config import CHATBOT_ENABLED
    if CHATBOT_ENABLED:
        from src.chatbot.mcp_client import mcp_client
        try:
            await mcp_client.start()
            logger.info(f"✓ Chatbot MCP: {len(mcp_client.tools)} tools disponíveis")
        except Exception as e:
            logger.warning(f"✗ Chatbot MCP falhou: {e}. Chat funcionará sem tools.")

    logger.info("=" * 60)
    logger.info(f"API rodando em: http://{HOST}:{PORT}")
    logger.info(f"Documentação: http://{HOST}:{PORT}/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Executado no encerramento da aplicação
    """
    logger.info("Encerrando Olist Logistics API")
    from src.chatbot.mcp_client import mcp_client
    from src.chatbot.openrouter_client import close_client
    await mcp_client.stop()
    await close_client()


# Exception handlers
@app.exception_handler(OlistAPIException)
async def olist_exception_handler(request: Request, exc: OlistAPIException):
    """
    Handler para exceções customizadas da aplicação
    """
    logger.error(f"OlistAPIException: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# Servir arquivos estáticos (HTML/CSS/JS) preservando as URIs relativas
static_path = Path(STATIC_DIR)
if static_path.exists():
    css_path = static_path / "css"
    js_path = static_path / "js"
    fonts_path = static_path / "fonts"
    
    if css_path.exists(): 
        app.mount("/css", StaticFiles(directory=str(css_path)), name="css")
    if js_path.exists():
        app.mount("/js", StaticFiles(directory=str(js_path)), name="js")
    if fonts_path.exists():
        app.mount("/fonts", StaticFiles(directory=str(fonts_path)), name="fonts")
        
    logger.info(f"✓ Arquivos estáticos montados diretamente na raiz")
else:
    logger.warning(
        f"✗ Diretório de estáticos não encontrado: {static_path}. "
        f"Crie a pasta e adicione os arquivos HTML/CSS/JS."
    )


# Rota raiz - Servir página inicial Frontend
@app.get("/", include_in_schema=False)
async def root():
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "Index.html não encontrado na pasta frontend!"}
        )

# Servir favicon.svg explicitamente
@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    fav_file = static_path / "favicon.svg"
    if fav_file.exists():
        return FileResponse(fav_file)
    return JSONResponse(status_code=404, content={"error": "Favicon não encontrado"})

# Executar aplicação (apenas para desenvolvimento)
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )
