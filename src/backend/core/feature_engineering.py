"""
Feature Engineering - Transformação de dados de entrada em features do V5 CatBoost
"""
import numpy as np
import pandas as pd
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from typing import Dict, Any

from backend.models.schemas import PedidoInput
from backend.core.data_loader import data_loader
from backend.utils.logger import get_logger
from backend.utils.exceptions import InvalidFeatureException
# Utils do MCP para estado
from olist_mcp.utils.state_mappings import get_state_from_cep

logger = get_logger(__name__)

# Lista Oficial exportada do Modelo V5
FEATURES_ORDER = [
    "velocidade_lojista_dias", "distancia_haversine_km", "freight_value",
    "volume_cm3", "product_weight_g", "price", "total_itens_pedido",
    "prazo_estimado_dias", "historico_atraso_vendedor", "qtd_pedidos_anteriores_vendedor",
    "frete_por_kg", "mes_compra", "semana_ano", "dia_semana_compra",
    "eh_alta_temporada", "seller_state", "customer_state", "rota",
    "product_category_name"
]

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    return R * (2 * asin(sqrt(a)))

def calcular_distancia(cep_cliente: str, cep_vendedor: str) -> float:
    coords_cliente = data_loader.get_cep_coordinates(cep_cliente)
    coords_vendedor = data_loader.get_cep_coordinates(cep_vendedor)
    
    if coords_cliente is None or coords_vendedor is None:
        logger.warning(f"Usando distância padrão. CEP não encontrado na db do Olist.")
        return 1000.0

    return haversine_distance(coords_cliente[0], coords_cliente[1], coords_vendedor[0], coords_vendedor[1])

def process_features(pedido: PedidoInput) -> pd.DataFrame:
    """Retorna DataFrame do Pandas pronto pro CatBoost V5."""
    try:
        dados = get_features_dict(pedido)
        # Cria DataFrame de linha única
        df = pd.DataFrame([dados])
        # Filtra e Ordena estritamente igual ao Treino
        return df[FEATURES_ORDER]
    except Exception as e:
        logger.error(f"Erro ao empacotar CatBoost DataFrame: {str(e)}")
        raise InvalidFeatureException(f"Pipeline Engineering Error: {str(e)}")

def get_features_dict(pedido: PedidoInput) -> Dict[str, Any]:
    """Computa features temporais, rotas e sazonais do V5 e retorna dicionário bruto"""
    try:
        distancia_km = calcular_distancia(pedido.cep_cliente, pedido.cep_vendedor)
        frete_por_kg = pedido.preco_frete / (pedido.peso_produto_g / 1000) if pedido.peso_produto_g > 0 else 0
        
        # Estados por CEP
        seller_state = get_state_from_cep(pedido.cep_vendedor)
        customer_state = get_state_from_cep(pedido.cep_cliente)
        
        # Sazonalidade
        try:
            dt = datetime.fromisoformat(pedido.data_aprovacao.replace("Z", "+00:00"))
            mes = dt.month
            sem = dt.isocalendar()[1]
            dia_sem = dt.weekday()
            # Alta temporada Olist: Nov (Black Friday) e Dez (Natal)
            alta = 1 if mes in [11, 12] else 0
        except:
            logger.warning("Falha no parse datetime. Padronizando p/ sem efeito sazonal.")
            mes, sem, dia_sem, alta = 6, 25, 3, 0

        # Montar Dict final com os Nomes Originais
        return {
            "velocidade_lojista_dias": float(pedido.velocidade_lojista_dias),
            "distancia_haversine_km": float(distancia_km),
            "freight_value": float(pedido.preco_frete),
            "volume_cm3": float(pedido.volume_cm3),
            "product_weight_g": float(pedido.peso_produto_g),
            "price": float(pedido.preco_produto),
            "total_itens_pedido": float(pedido.total_itens_pedido),
            "prazo_estimado_dias": float(pedido.prazo_estimado_dias),
            "historico_atraso_vendedor": float(pedido.historico_atraso_vendedor),
            "qtd_pedidos_anteriores_vendedor": float(pedido.qtd_pedidos_anteriores_vendedor),
            "frete_por_kg": float(frete_por_kg),
            "mes_compra": int(mes),
            "semana_ano": int(sem),
            "dia_semana_compra": int(dia_sem),
            "eh_alta_temporada": int(alta),
            "seller_state": seller_state,
            "customer_state": customer_state,
            "rota": f"{seller_state}-{customer_state}",
            "product_category_name": pedido.categoria_produto
        }
    except Exception as e:
        logger.error(f"Erro grave ao montar Feature Dict V5: {str(e)}")
        raise e
