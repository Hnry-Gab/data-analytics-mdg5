"""
Feature Engineering - Transformação de dados de entrada em features do modelo
"""
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from typing import Dict, Any
from src.models.schemas import PedidoInput
from src.core.data_loader import data_loader
from src.utils.logger import get_logger
from src.utils.exceptions import InvalidFeatureException, CEPNotFoundException

logger = get_logger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distância geodésica entre dois pontos (lat, lng) em km usando Haversine

    Args:
        lat1: Latitude do ponto 1
        lon1: Longitude do ponto 1
        lat2: Latitude do ponto 2
        lon2: Longitude do ponto 2

    Returns:
        Distância em quilômetros
    """
    # Raio da Terra em km
    R = 6371.0

    # Converter para radianos
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Diferenças
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # Distância em km
    distance = R * c

    return distance


def calcular_distancia(cep_cliente: str, cep_vendedor: str) -> float:
    """
    Calcula distância entre cliente e vendedor baseado nos CEPs

    Args:
        cep_cliente: CEP do cliente (8 dígitos)
        cep_vendedor: CEP do vendedor (8 dígitos)

    Returns:
        Distância em quilômetros

    Raises:
        CEPNotFoundException: Se algum CEP não for encontrado
    """
    # Buscar coordenadas na base de geolocalização
    coords_cliente = data_loader.get_cep_coordinates(cep_cliente)
    coords_vendedor = data_loader.get_cep_coordinates(cep_vendedor)

    # Se não encontrar, usar distância média estimada
    if coords_cliente is None or coords_vendedor is None:
        logger.warning(
            f"CEP não encontrado (Cliente: {cep_cliente}, Vendedor: {cep_vendedor}). "
            f"Usando distância padrão."
        )
        # Distância média do Brasil: ~1000km
        return 1000.0

    # Calcular distância usando Haversine
    lat1, lng1 = coords_cliente
    lat2, lng2 = coords_vendedor

    distance = haversine_distance(lat1, lng1, lat2, lng2)
    logger.debug(f"Distância calculada: {distance:.2f} km")

    return distance


def encode_categoria(categoria: str) -> int:
    """
    Encoda categoria de produto para valor numérico

    Args:
        categoria: Nome da categoria (ex: 'eletronicos', 'moda')

    Returns:
        Código numérico da categoria
    """
    # Mapeamento básico de categorias
    # TODO: Substituir por mapeamento real do dataset histórico
    categorias_map = {
        'eletronicos': 1,
        'moveis': 2,
        'esporte': 3,
        'beleza': 4,
        'moda': 5,
        'casa': 6,
        'alimentos': 7,
        'brinquedos': 8,
        'automotivo': 9,
        'livros': 10,
        'outros': 0
    }

    categoria_lower = categoria.lower().strip()
    encoded = categorias_map.get(categoria_lower, 0)

    logger.debug(f"Categoria '{categoria}' encodada como {encoded}")

    return encoded


def process_features(pedido: PedidoInput) -> np.ndarray:
    """
    Converte PedidoInput em array de features para o modelo XGBoost

    Etapas:
    1. Calcular distância entre cliente e vendedor
    2. Encodar categoria do produto
    3. Criar features derivadas (ex: preco_por_peso)
    4. Montar array na ordem esperada pelo modelo

    Args:
        pedido: Dados de entrada validados

    Returns:
        Array numpy com features processadas (shape: 1, n_features)

    Raises:
        InvalidFeatureException: Se houver erro no processamento
    """
    try:
        # 1. Calcular distância
        distancia_km = calcular_distancia(
            pedido.cep_cliente,
            pedido.cep_vendedor
        )

        # 2. Encodar categoria
        categoria_encoded = encode_categoria(pedido.categoria_produto)

        # 3. Features derivadas
        preco_por_peso = (
            pedido.preco_frete / pedido.peso_produto_kg
            if pedido.peso_produto_kg > 0 else 0
        )
        densidade = (
            pedido.peso_produto_kg / (pedido.peso_produto_volume_cm3 / 1000000)  # cm3 -> m3
            if pedido.peso_produto_volume_cm3 > 0 else 0
        )

        # 4. Montar dicionário de features
        features_dict = {
            "distancia_km": distancia_km,
            "categoria_encoded": categoria_encoded,
            "peso_kg": pedido.peso_produto_kg,
            "preco_frete": pedido.preco_frete,
            "volume_cm3": pedido.peso_produto_volume_cm3,
            "preco_por_peso": preco_por_peso,
            "densidade_kg_m3": densidade,
        }

        # 5. Converter para DataFrame (ordem das colunas importa!)
        # TODO: Ajustar ordem conforme spec/data_schema.md quando disponível
        df = pd.DataFrame([features_dict])

        # 6. Retornar como array numpy
        features_array = df.values

        logger.debug(f"Features processadas: {features_dict}")

        return features_array

    except Exception as e:
        logger.error(f"Erro ao processar features: {str(e)}")
        raise InvalidFeatureException(f"Erro ao processar features: {str(e)}")


def get_features_dict(pedido: PedidoInput) -> Dict[str, Any]:
    """
    Retorna dicionário de features processadas (para debug/resposta)

    Args:
        pedido: Dados de entrada validados

    Returns:
        Dicionário com features processadas
    """
    try:
        distancia_km = calcular_distancia(pedido.cep_cliente, pedido.cep_vendedor)
        categoria_encoded = encode_categoria(pedido.categoria_produto)
        preco_por_peso = pedido.preco_frete / pedido.peso_produto_kg if pedido.peso_produto_kg > 0 else 0
        densidade = pedido.peso_produto_kg / (pedido.peso_produto_volume_cm3 / 1000000) if pedido.peso_produto_volume_cm3 > 0 else 0

        return {
            "distancia_km": round(distancia_km, 2),
            "categoria_encoded": categoria_encoded,
            "categoria_original": pedido.categoria_produto,
            "peso_kg": pedido.peso_produto_kg,
            "preco_frete": pedido.preco_frete,
            "volume_cm3": pedido.peso_produto_volume_cm3,
            "preco_por_peso": round(preco_por_peso, 2),
            "densidade_kg_m3": round(densidade, 2),
        }
    except Exception as e:
        logger.error(f"Erro ao gerar dicionário de features: {str(e)}")
        return {}
