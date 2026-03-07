"""
Carregamento e gerenciamento dos dados históricos (CSV)
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict
from src.config import CSV_PATH
from src.utils.logger import get_logger
from src.utils.exceptions import DataNotLoadedException

logger = get_logger(__name__)


class DataLoader:
    """
    Singleton para carregar e cachear dados históricos em memória
    """
    _instance: Optional['DataLoader'] = None
    _data: Optional[pd.DataFrame] = None
    _geolocation: Optional[pd.DataFrame] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_csv(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        if self._data is not None:
            logger.info("Dados já carregados em memória")
            return self._data
            
        base_dir = Path(CSV_PATH)
        orders_file = base_dir / "olist_orders_dataset.csv"
        items_file = base_dir / "olist_order_items_dataset.csv"
        customers_file = base_dir / "olist_customers_dataset.csv"
        products_file = base_dir / "olist_products_dataset.csv"
        sellers_file = base_dir / "olist_sellers_dataset.csv"

        if not orders_file.exists() or not items_file.exists() or not customers_file.exists():
            logger.warning(
                f"Tabelas essenciais não encontradas em: {base_dir}. "
                f"Dashboard ficará com visual apenas estético."
            )
            return pd.DataFrame()

        try:
            logger.info("Lendo e agregando datasets brutos de pedidos, itens e clientes.")
            df_orders = pd.read_csv(orders_file)
            df_items = pd.read_csv(items_file)
            df_customers = pd.read_csv(customers_file)
            df_products = pd.read_csv(products_file) if products_file.exists() else pd.DataFrame()
            df_sellers = pd.read_csv(sellers_file) if sellers_file.exists() else pd.DataFrame()
            
            # Merge para pegar Freight (itens) e State (clientes)
            df_merged = df_orders.merge(df_items, on="order_id", how="left")
            df_merged = df_merged.merge(df_customers, on="customer_id", how="left")
            if not df_products.empty:
                df_merged = df_merged.merge(df_products, on="product_id", how="left")
            if not df_sellers.empty:
                df_merged = df_merged.merge(df_sellers, on="seller_id", how="left")
            
            # Tratar datas
            df_merged['order_purchase_timestamp'] = pd.to_datetime(df_merged['order_purchase_timestamp'])
            df_merged['order_approved_at'] = pd.to_datetime(df_merged['order_approved_at'])
            df_merged['order_delivered_carrier_date'] = pd.to_datetime(df_merged['order_delivered_carrier_date'])
            df_merged['purchase_year'] = df_merged['order_purchase_timestamp'].dt.year
            
            # Feature "delivery_delayed" e Cálculo de Delta Dias
            if "order_delivered_customer_date" in df_merged.columns and "order_estimated_delivery_date" in df_merged.columns:
                delivered = pd.to_datetime(df_merged['order_delivered_customer_date'])
                estimated = pd.to_datetime(df_merged['order_estimated_delivery_date'])
                
                # Target binário
                df_merged['delivery_delayed'] = (delivered > estimated).astype(int)
                
                # Delta em dias (Positivo = Atraso, Negativo = Antecipação)
                df_merged['delta_days'] = (delivered - estimated).dt.days
            else:
                df_merged['delivery_delayed'] = 0
                df_merged['delta_days'] = 0
                
            # Velocidade do Lojista
            df_merged['velocidade_lojista_dias'] = (df_merged['order_delivered_carrier_date'] - df_merged['order_approved_at']).dt.days
            df_merged['velocidade_lojista_dias'] = df_merged['velocidade_lojista_dias'].fillna(
                df_merged['velocidade_lojista_dias'].median() if not df_merged['velocidade_lojista_dias'].isna().all() else 1.0
            )
            
            # Macro-regiões
            regioes_map = {
                'AM': 'Norte', 'RR': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'TO': 'Norte', 'RO': 'Norte', 'AC': 'Norte',
                'MA': 'Nordeste', 'PI': 'Nordeste', 'CE': 'Nordeste', 'RN': 'Nordeste', 'PE': 'Nordeste', 'PB': 'Nordeste', 'SE': 'Nordeste', 'AL': 'Nordeste', 'BA': 'Nordeste',
                'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'DF': 'Centro-Oeste',
                'SP': 'Sudeste', 'RJ': 'Sudeste', 'ES': 'Sudeste', 'MG': 'Sudeste',
                'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
            }
            if 'customer_state' in df_merged.columns:
                df_merged['customer_regiao'] = df_merged['customer_state'].map(regioes_map)
            if 'seller_state' in df_merged.columns:
                df_merged['seller_regiao'] = df_merged['seller_state'].map(regioes_map)

            self._data = df_merged
            logger.info(f"Dados históricos carregados: {len(self._data)} linhas (Merged c/ Clientes, Produtos e Sellers)")
            return self._data
        except Exception as e:
            logger.error(f"Erro ao agregar csv brutos: {str(e)}")
            raise DataNotLoadedException(f"Erro ao carregar dados brutos on the fly: {str(e)}")

    def load_geolocation(self, geo_path: Optional[str] = None) -> pd.DataFrame:
        """
        Carrega dados de geolocalização (CEP -> lat/lng)

        Args:
            geo_path: Caminho para o CSV de geolocalização

        Returns:
            DataFrame com dados de geolocalização

        Raises:
            FileNotFoundError: Se o arquivo não existir
        """
        if self._geolocation is not None:
            logger.info("Geolocalização já carregada em memória")
            return self._geolocation

        # Tentar carregar do caminho fornecido ou caminho padrão
        if geo_path:
            geo_file = Path(geo_path)
        else:
            # Assumir que está na mesma pasta do CSV de dados
            csv_dir = Path(CSV_PATH)
            geo_file = csv_dir / "olist_geolocation_dataset.csv"

        if not geo_file.exists():
            logger.warning(
                f"Geolocalização não encontrada em: {geo_file}. "
                f"Distâncias não serão calculadas com precisão."
            )
            return pd.DataFrame()

        try:
            logger.info(f"Carregando geolocalização de: {geo_file}")
            self._geolocation = pd.read_csv(geo_file)
            logger.info(f"Geolocalização carregada: {len(self._geolocation)} registros")
            return self._geolocation
        except Exception as e:
            logger.error(f"Erro ao carregar geolocalização: {str(e)}")
            return pd.DataFrame()

    def get_feature_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Retorna estatísticas descritivas para normalização

        Returns:
            Dicionário com média e desvio padrão de cada feature numérica
        """
        if self._data is None or self._data.empty:
            logger.warning("Dados não carregados, retornando estatísticas vazias")
            return {}

        numeric_cols = self._data.select_dtypes(include=['float64', 'int64']).columns

        stats = {
            "mean": self._data[numeric_cols].mean().to_dict(),
            "std": self._data[numeric_cols].std().to_dict(),
            "min": self._data[numeric_cols].min().to_dict(),
            "max": self._data[numeric_cols].max().to_dict(),
        }

        return stats

    def get_cep_coordinates(self, cep: str) -> Optional[tuple[float, float]]:
        """
        Retorna coordenadas (latitude, longitude) de um CEP

        Args:
            cep: CEP com 8 dígitos

        Returns:
            Tupla (lat, lng) ou None se não encontrado
        """
        if self._geolocation is None or self._geolocation.empty:
            logger.warning("Geolocalização não disponível")
            return None

        # Converter CEP para prefixo (5 primeiros dígitos)
        cep_prefix = cep[:5]

        # Buscar no dataset
        matches = self._geolocation[
            self._geolocation['geolocation_zip_code_prefix'].astype(str) == cep_prefix
        ]

        if matches.empty:
            logger.debug(f"CEP {cep} não encontrado na geolocalização")
            return None

        # Retornar primeira ocorrência
        row = matches.iloc[0]
        lat = row['geolocation_lat']
        lng = row['geolocation_lng']

        return (float(lat), float(lng))

    def is_loaded(self) -> bool:
        """
        Verifica se os dados estão carregados

        Returns:
            True se os dados estão carregados, False caso contrário
        """
        return self._data is not None and not self._data.empty


# Singleton global
data_loader = DataLoader()
