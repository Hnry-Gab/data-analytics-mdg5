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
    "/insights",
    status_code=status.HTTP_200_OK,
    summary="Obter dados reais para a aba de Insights baseados na EDA"
)
async def get_insights_data():
    if not data_loader.is_loaded() or data_loader._data is None:
        return {"error": "Dataset não carregado."}
        
    df = data_loader._data.copy()
    
    # 1. Interstate Routes (Donut)
    df_valid = df.dropna(subset=['seller_state', 'customer_state', 'delivery_delayed']).copy()
    df_valid['is_interstate'] = df_valid['seller_state'] != df_valid['customer_state']
    
    inter_total = df_valid['is_interstate'].sum()
    intra_total = (~df_valid['is_interstate']).sum()
    
    inter_delayed = df_valid[df_valid['is_interstate']]['delivery_delayed'].sum()
    intra_delayed = df_valid[~df_valid['is_interstate']]['delivery_delayed'].sum()
    
    inter_ontime = inter_total - inter_delayed
    intra_ontime = intra_total - intra_delayed
    
    inter_rate = (inter_delayed / inter_total * 100) if inter_total > 0 else 0
    intra_rate = (intra_delayed / intra_total * 100) if intra_total > 0 else 0
    
    donut_data = {
        "inter_rate": round(inter_rate, 1),
        "intra_rate": round(intra_rate, 1),
        "inter_delayed": int(inter_delayed),
        "inter_ontime": int(inter_ontime),
        "intra_delayed": int(intra_delayed),
        "intra_ontime": int(intra_ontime)
    }
    
    # 2. Critical Categories (Treemap)
    if 'product_category_name' in df.columns:
        cat_stats = df.groupby('product_category_name').agg(
            total=('order_id', 'count'),
            delayed=('delivery_delayed', 'sum')
        ).reset_index()
        cat_stats = cat_stats[cat_stats['total'] >= 100]
        cat_stats['delay_rate'] = (cat_stats['delayed'] / cat_stats['total']) * 100
        cat_stats = cat_stats.sort_values('delay_rate', ascending=False).head(12)
        
        treemap_data = {
            "categories": cat_stats['product_category_name'].tolist(),
            "totals": int_to_list(cat_stats['total']),
            "delay_rates": [round(x, 1) for x in cat_stats['delay_rate'].tolist()]
        }
    else:
        treemap_data = {"categories": [], "totals": [], "delay_rates": []}
        
    # 3. Seller Bottleneck (Violin)
    if 'velocidade_lojista_dias' in df.columns:
        df_violin = df[['velocidade_lojista_dias', 'delivery_delayed']].dropna()
        df_ontime = df_violin[df_violin['delivery_delayed'] == 0]['velocidade_lojista_dias']
        df_delayed = df_violin[df_violin['delivery_delayed'] == 1]['velocidade_lojista_dias']
        
        df_ontime = df_ontime[df_ontime <= 30]
        df_delayed = df_delayed[df_delayed <= 30]
        
        violin_data = {
            "on_time": df_ontime.sample(min(1000, len(df_ontime)), random_state=42).tolist() if len(df_ontime) > 0 else [],
            "delayed": df_delayed.sample(min(1000, len(df_delayed)), random_state=42).tolist() if len(df_delayed) > 0 else []
        }
    else:
        violin_data = {"on_time": [], "delayed": []}
        
    # 4. Freight Economics (Scatter)
    if 'price' in df.columns and 'freight_value' in df.columns:
        df_scatter = df[['price', 'freight_value', 'delivery_delayed']].dropna().copy()
        df_scatter = df_scatter[(df_scatter['price'] < 3000) & (df_scatter['freight_value'] < 300)]
        df_scatter['freight_ratio'] = df_scatter['freight_value'] / df_scatter['price']
        import numpy as np
        df_scatter['freight_ratio'] = df_scatter['freight_ratio'].replace([np.inf, -np.inf], 0)
        df_scatter = df_scatter[df_scatter['freight_ratio'] <= 2.0]
        
        df_scatter_s = df_scatter.sample(min(1500, len(df_scatter)), random_state=42)
        
        scatter_data = {
            "on_time_x": df_scatter_s[df_scatter_s['delivery_delayed'] == 0]['price'].tolist(),
            "on_time_y": df_scatter_s[df_scatter_s['delivery_delayed'] == 0]['freight_ratio'].round(2).tolist(),
            "delayed_x": df_scatter_s[df_scatter_s['delivery_delayed'] == 1]['price'].tolist(),
            "delayed_y": df_scatter_s[df_scatter_s['delivery_delayed'] == 1]['freight_ratio'].round(2).tolist()
        }
    else:
        scatter_data = {"on_time_x": [], "on_time_y": [], "delayed_x": [], "delayed_y": []}
        
    # 5. Macro-Regiões (Heatmap)
    heatmap_data = {"x": [], "y": [], "z": []}
    if 'seller_regiao' in df.columns and 'customer_regiao' in df.columns:
        regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
        heatmap_data['x'] = regioes # Destino
        heatmap_data['y'] = regioes # Origem
        
        z_matrix = []
        for origin in regioes:
            row = []
            for dest in regioes:
                mask = (df['seller_regiao'] == origin) & (df['customer_regiao'] == dest)
                subset = df[mask]
                if len(subset) >= 50:
                    rate = subset['delivery_delayed'].mean() * 100
                    row.append(round(rate, 1))
                else:
                    row.append(None)
            z_matrix.append(row)
            
        heatmap_data['z'] = z_matrix

    return {
        "donut": donut_data,
        "treemap": treemap_data,
        "violin": violin_data,
        "scatter": scatter_data,
        "heatmap": heatmap_data
    }

def int_to_list(series):
    return [int(x) for x in series.tolist()]


@router.get(
    "/insights/temporal",
    status_code=status.HTTP_200_OK,
    summary="Análise temporal de atrasos (conforme notebook dia1_alpha_pipeline)"
)
async def get_temporal_insights():
    """Retorna análises temporais: taxa de atraso por mês, dia da semana e série temporal."""
    if not data_loader.is_loaded() or data_loader._data is None:
        return {"error": "Dataset não carregado."}

    df = data_loader._data.copy()

    # Taxa de atraso por mês do ano
    if 'mes_compra' in df.columns:
        atraso_mes = df.groupby('mes_compra').agg(
            total=('order_id', 'count'),
            taxa_atraso=('delivery_delayed', 'mean')
        ).reset_index()
        mes_data = {
            "meses": atraso_mes['mes_compra'].tolist(),
            "taxas": [round(x * 100, 1) for x in atraso_mes['taxa_atraso'].tolist()],
            "totais": atraso_mes['total'].tolist()
        }
    else:
        mes_data = {"meses": [], "taxas": [], "totais": []}

    # Taxa de atraso por dia da semana
    if 'dia_semana_compra' in df.columns:
        atraso_dia = df.groupby('dia_semana_compra').agg(
            total=('order_id', 'count'),
            taxa_atraso=('delivery_delayed', 'mean')
        ).reset_index()
        dia_data = {
            "dias": atraso_dia['dia_semana_compra'].tolist(),
            "taxas": [round(x * 100, 1) for x in atraso_dia['taxa_atraso'].tolist()],
            "totais": atraso_dia['total'].tolist()
        }
    else:
        dia_data = {"dias": [], "taxas": [], "totais": []}

    # Série temporal mensal (evolução ao longo do tempo)
    if 'order_purchase_timestamp' in df.columns:
        df['ano_mes'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
        serie_mensal = df.groupby('ano_mes').agg(
            total=('order_id', 'count'),
            taxa_atraso=('delivery_delayed', 'mean')
        ).reset_index()
        # Filtrar meses com poucos pedidos
        serie_mensal = serie_mensal[serie_mensal['total'] >= 100]

        serie_data = {
            "meses": serie_mensal['ano_mes'].tolist(),
            "taxas": [round(x * 100, 1) for x in serie_mensal['taxa_atraso'].tolist()],
            "volumes": serie_mensal['total'].tolist()
        }
    else:
        serie_data = {"meses": [], "taxas": [], "volumes": []}

    return {
        "mes": mes_data,
        "dia_semana": dia_data,
        "serie_temporal": serie_data
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
