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
    description="Prediz a probabilidade de atraso de um pedido usando CatBoost V5"
)
async def predict_delay(pedido: PedidoInput) -> PredictionOutput:
    try:
        logger.info(f"Nova predição V5 solicitada via API p/ rota {pedido.cep_vendedor}->{pedido.cep_cliente}!")

        # 1. Obter DataFrame de teste c/ 19 features rigorosas
        features_df = process_features(pedido)
        
        # Obter dicionário cru p/ response
        features_dict = get_features_dict(pedido)

        # 2. Invocar Modelo C++ Nativo (CatBoost) -> (prob, confianca_bruta, classe_str)
        prob, conf_bruta, classe = ml_model.predict_proba(features_df)
        
        # 3. Formatar saída percentual
        prob_percent = prob * 100
        confianca = conf_bruta * 100
        limiar = ml_model._config.get('threshold', 0.5) * 100

        logger.info(
            f"Predição concluída: {classe} "
            f"(probabilidade: {prob_percent:.2f}%)"
        )

        return PredictionOutput(
            probabilidade_atraso=round(prob_percent, 2),
            classe_predicao=classe,
            confianca=round(confianca, 2),
            limiar_corte=round(limiar, 2),
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
    description="Retorna a lista de chaves JSON necessárias na predição V5"
)
async def get_available_features() -> FeaturesResponse:
    logger.debug("Listando features disponíveis")
    return FeaturesResponse(
        features=[
            "cep_cliente", "cep_vendedor", "categoria_produto", "peso_produto_g",
            "preco_produto", "preco_frete", "volume_cm3", "total_itens_pedido",
            "prazo_estimado_dias", "velocidade_lojista_dias", "historico_atraso_vendedor",
            "qtd_pedidos_anteriores_vendedor", "data_aprovacao"
        ],
        description="Payload obrigatório p/ endpoints preditivos do V5"
    )

@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Obter estatísticas filtradas do Dashboard"
)
async def get_dashboard_stats(state: str = None, year: int = None):
    """Retorna KPIs e dados para gráficos filtrados por estado e ano."""
    if not data_loader.is_loaded() or data_loader._data is None:
        return {"error": "Dataset não carregado."}

    df = data_loader._data.copy()
    target_col = "delivery_delayed"
    
    # 1. Aplicar Filtros
    if state:
        df = df[df['customer_state'] == state]
    if year:
        df = df[df['purchase_year'] == year]

    total_orders = len(df)
    if total_orders == 0:
        return {
            "total_orders": 0, "delayed_orders": 0, "delay_rate": 0, "avg_freight": 0,
            "map_data": {}, "ranking_data": [], "timeline_data": {"x": [], "y": []}
        }

    # 2. KPIs
    delayed_orders = int(df[target_col].sum())
    avg_freight = float(df['freight_value'].mean())
    delay_rate = round((delayed_orders / total_orders * 100), 1)
    # Média de Delta Dias
    avg_delta = float(df['delta_days'].mean()) if 'delta_days' in df.columns else 0.0

    # 2.1 Média Global (Ignorando Filtro de Estado, respeitando apenas Ano)
    df_global = data_loader._data.copy()
    if year:
        df_global = df_global[df_global['purchase_year'] == year]
    global_delay_rate = round((df_global[target_col].sum() / len(df_global) * 100), 1) if len(df_global) > 0 else 0

    # 3. Dados para o Mapa
    map_df = df.groupby('customer_state')[target_col].mean() * 100
    map_data = map_df.to_dict()

    # 4. Ranking
    rank_df = df.groupby('customer_state')[target_col].mean().sort_values(ascending=False).head(10) * 100
    ranking_data = [{"state": s, "rate": round(r, 1)} for s, r in rank_df.items()]

    # 5. Timeline
    df['month_year'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    timeline_df = df.groupby('month_year')[target_col].mean().sort_index() * 100
    timeline_data = {
        "x": timeline_df.index.tolist(),
        "y": [round(v, 1) for v in timeline_df.values]
    }

    return {
        "total_orders": total_orders,
        "delayed_orders": delayed_orders,
        "delay_rate": delay_rate,
        "global_delay_rate": global_delay_rate,
        "avg_freight": round(avg_freight, 2),
        "delta_days": round(avg_delta, 1),
        "map_data": map_data,
        "ranking_data": ranking_data,
        "timeline_data": timeline_data
    }

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar status da API"
)
async def health_check() -> HealthResponse:
    model_loaded = ml_model.is_loaded()
    data_loaded = data_loader.is_loaded()

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
