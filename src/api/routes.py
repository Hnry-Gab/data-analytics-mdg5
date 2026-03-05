"""
Endpoints REST da API Olist Logistics
"""
from fastapi import APIRouter, HTTPException, status
from src.models.schemas import (
    PedidoInput,
    PredictionOutput,
    HealthResponse,
    FeaturesResponse
)
from src.core.ml_model import ml_model
from src.core.data_loader import data_loader
from src.core.feature_engineering import process_features, get_features_dict
from src.utils.logger import get_logger
from src.utils.exceptions import (
    ModelNotLoadedException,
    InvalidFeatureException,
    PredictionException
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["Predição de Atraso"])


@router.post(
    "/predict",
    response_model=PredictionOutput,
    status_code=status.HTTP_200_OK,
    summary="Prever atraso de entrega",
    description="Prediz a probabilidade de atraso de um pedido com base nas características fornecidas"
)
async def predict_delay(pedido: PedidoInput) -> PredictionOutput:
    """
    Endpoint principal de predição de atraso

    **Entrada:**
    - CEP cliente e vendedor
    - Categoria do produto
    - Peso, frete e volume

    **Saída:**
    - Probabilidade de atraso (0-100%)
    - Classe de predição (No Prazo / Atrasado)
    - Confiança da predição
    - Features utilizadas

    **Erros possíveis:**
    - 400: Dados de entrada inválidos
    - 503: Modelo não carregado
    - 500: Erro interno na predição
    """
    try:
        logger.info(f"Nova predição solicitada para categoria: {pedido.categoria_produto}")

        # 1. Processar features
        features_array = process_features(pedido)
        features_dict = get_features_dict(pedido)

        # 2. Invocar modelo XGBoost
        prob_atraso = ml_model.predict_proba(features_array)
        prob_percent = prob_atraso * 100

        # 3. Determinar classe e confiança
        classe = "Atrasado" if prob_percent > 50 else "No Prazo"
        confianca = max(prob_atraso, 1 - prob_atraso) * 100

        logger.info(
            f"Predição concluída: {classe} "
            f"(probabilidade: {prob_percent:.2f}%, confiança: {confianca:.2f}%)"
        )

        # 4. Retornar resultado
        return PredictionOutput(
            probabilidade_atraso=round(prob_percent, 2),
            classe_predicao=classe,
            confianca=round(confianca, 2),
            features_utilizadas=features_dict
        )

    except InvalidFeatureException as e:
        logger.error(f"Erro de validação de features: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Features inválidas: {str(e)}"
        )

    except ModelNotLoadedException as e:
        logger.error(f"Modelo não carregado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo de ML não está disponível. Tente novamente mais tarde."
        )

    except PredictionException as e:
        logger.error(f"Erro na predição: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao realizar predição: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/features",
    response_model=FeaturesResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar features aceitas",
    description="Retorna a lista de features necessárias para realizar uma predição"
)
async def get_available_features() -> FeaturesResponse:
    """
    Lista todas as features de entrada aceitas pela API

    **Saída:**
    - Lista de nomes de features
    - Descrição do uso
    """
    logger.debug("Listando features disponíveis")

    return FeaturesResponse(
        features=[
            "cep_cliente",
            "cep_vendedor",
            "categoria_produto",
            "peso_produto_kg",
            "preco_frete",
            "peso_produto_volume_cm3"
        ],
        description="Features obrigatórias para predição de atraso. "
                    "Todas devem ser fornecidas no endpoint /api/predict"
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar status da API",
    description="Health check para verificar se o modelo e dados estão carregados"
)
async def health_check() -> HealthResponse:
    """
    Health check da aplicação

    **Saída:**
    - Status geral (healthy/unhealthy)
    - Se modelo ML está carregado
    - Se dados históricos estão carregados
    """
    model_loaded = ml_model.is_loaded()
    data_loaded = data_loader.is_loaded()

    # Status é healthy se pelo menos o modelo estiver carregado
    # (dados históricos são opcionais)
    is_healthy = model_loaded

    status_str = "healthy" if is_healthy else "unhealthy"

    logger.info(
        f"Health check: {status_str} "
        f"(modelo: {model_loaded}, dados: {data_loaded})"
    )

    return HealthResponse(
        status=status_str,
        model_loaded=model_loaded,
        data_loaded=data_loaded
    )
