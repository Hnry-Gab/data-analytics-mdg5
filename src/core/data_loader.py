"""
Carregamento e gerenciamento dos dados históricos (CSV)
"""
import pandas as pd
import numpy as np
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

            # LIMPEZA 1: Filtrar apenas pedidos ENTREGUES (conforme notebook)
            linhas_antes_filtro = len(df_orders)
            df_orders = df_orders[df_orders['order_status'] == 'delivered'].copy()
            logger.info(f"Filtro status='delivered': {linhas_antes_filtro} -> {len(df_orders)} pedidos")

            # LIMPEZA 2: Remover pedidos sem data de entrega real
            if 'order_delivered_customer_date' in df_orders.columns:
                nulos_entrega = df_orders['order_delivered_customer_date'].isna().sum()
                df_orders = df_orders.dropna(subset=['order_delivered_customer_date'])
                logger.info(f"Removidos {nulos_entrega} pedidos sem data de entrega")

            # LIMPEZA 3: Tratar valores faltantes em produtos
            if not df_products.empty:
                # Categoria faltante
                df_products['product_category_name'] = df_products['product_category_name'].fillna('desconhecido')

                # Dimensões com mediana
                cols_numericas = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
                for col in cols_numericas:
                    if col in df_products.columns and df_products[col].isna().sum() > 0:
                        mediana = df_products[col].median()
                        df_products[col] = df_products[col].fillna(mediana)
                        logger.info(f"  {col}: preenchido com mediana = {mediana}")

                logger.info("Tratamento de nulos em products concluído")
            
            # MERGE: Unificar todas as tabelas
            df_merged = df_orders.merge(df_items, on="order_id", how="left")
            df_merged = df_merged.merge(df_customers, on="customer_id", how="left")
            if not df_products.empty:
                df_merged = df_merged.merge(df_products, on="product_id", how="left")
            if not df_sellers.empty:
                df_merged = df_merged.merge(df_sellers, on="seller_id", how="left")

            # MERGE COM PAYMENTS: Adicionar tipo de pagamento principal
            payments_file = base_dir / "olist_order_payments_dataset.csv"
            if payments_file.exists():
                df_payments = pd.read_csv(payments_file)
                # Extrair tipo de pagamento principal (maior valor)
                payments_sorted = df_payments.sort_values(by=['order_id', 'payment_value'], ascending=[True, False])
                payments_agg = payments_sorted.drop_duplicates(subset=['order_id'], keep='first')[['order_id', 'payment_type']]

                df_merged = df_merged.merge(
                    payments_agg.rename(columns={'payment_type': 'tipo_pagamento_principal'}),
                    on='order_id',
                    how='left'
                )
                df_merged['tipo_pagamento_principal'] = df_merged['tipo_pagamento_principal'].fillna('desconhecido')
                logger.info(f"Merge com payments concluído: tipo_pagamento_principal adicionado")
            
            # Tratar datas
            df_merged['order_purchase_timestamp'] = pd.to_datetime(df_merged['order_purchase_timestamp'])
            df_merged['order_approved_at'] = pd.to_datetime(df_merged['order_approved_at'])
            df_merged['order_delivered_carrier_date'] = pd.to_datetime(df_merged['order_delivered_carrier_date'])
            df_merged['order_delivered_customer_date'] = pd.to_datetime(df_merged['order_delivered_customer_date'])
            df_merged['order_estimated_delivery_date'] = pd.to_datetime(df_merged['order_estimated_delivery_date'])
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

            # MERGE COM GEOLOCALIZAÇÃO: Adicionar coordenadas de vendedor e cliente
            geo = self.load_geolocation()
            if not geo.empty:
                # Deduplicar geolocalização por CEP (média de lat/lng)
                geo_agg = (
                    geo
                    .groupby('geolocation_zip_code_prefix', as_index=False)
                    .agg({'geolocation_lat': 'mean', 'geolocation_lng': 'mean'})
                )
                logger.info(f"Geolocalização agregada: {len(geo)} -> {len(geo_agg)} CEPs únicos")

                # Merge geolocalização do VENDEDOR
                df_merged = df_merged.merge(
                    geo_agg.rename(columns={
                        'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
                        'geolocation_lat': 'seller_lat',
                        'geolocation_lng': 'seller_lng'
                    }),
                    on='seller_zip_code_prefix',
                    how='left'
                )

                # Merge geolocalização do CLIENTE
                df_merged = df_merged.merge(
                    geo_agg.rename(columns={
                        'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
                        'geolocation_lat': 'customer_lat',
                        'geolocation_lng': 'customer_lng'
                    }),
                    on='customer_zip_code_prefix',
                    how='left'
                )

                # Preencher coordenadas faltantes com mediana
                for col in ['seller_lat', 'seller_lng', 'customer_lat', 'customer_lng']:
                    if col in df_merged.columns:
                        mediana = df_merged[col].median()
                        df_merged[col] = df_merged[col].fillna(mediana)

                logger.info("Merge com geolocalização concluído")

            # FEATURES DERIVADAS (conforme notebook dia1_alpha_pipeline)

            # Feature 1: frete_ratio
            df_merged['frete_ratio'] = df_merged['freight_value'] / df_merged['price']
            df_merged['frete_ratio'] = df_merged['frete_ratio'].replace([np.inf, -np.inf], np.nan).fillna(0)

            # Feature 2: dia_semana_compra (0=Segunda, 6=Domingo)
            df_merged['dia_semana_compra'] = df_merged['order_purchase_timestamp'].dt.dayofweek

            # Feature 3: rota_interestadual
            if 'seller_state' in df_merged.columns and 'customer_state' in df_merged.columns:
                df_merged['rota_interestadual'] = (df_merged['seller_state'] != df_merged['customer_state']).astype(int)

            # Feature 4: total_itens_pedido
            df_merged['total_itens_pedido'] = df_merged.groupby('order_id')['order_item_id'].transform('max')
            df_merged['total_itens_pedido'] = df_merged['total_itens_pedido'].fillna(1).astype(int)

            # Feature 5: ticket_medio_alto (>= R$500)
            df_merged['ticket_medio_alto'] = (df_merged['price'] >= 500.0).astype(int)

            # Feature 6: historico_atraso_seller (expanding window - anti-leakage)
            df_merged = df_merged.sort_values('order_purchase_timestamp').reset_index(drop=True)
            df_merged['historico_atraso_seller'] = (
                df_merged.groupby('seller_id')['delivery_delayed']
                .transform(lambda x: x.expanding().mean().shift(1))
            )
            media_global_atraso = df_merged['delivery_delayed'].mean()
            df_merged['historico_atraso_seller'] = df_merged['historico_atraso_seller'].fillna(media_global_atraso)

            # Feature 7: velocidade_transportadora_dias
            if 'order_delivered_customer_date' in df_merged.columns and 'order_delivered_carrier_date' in df_merged.columns:
                df_merged['velocidade_transportadora_dias'] = (
                    df_merged['order_delivered_customer_date'] - df_merged['order_delivered_carrier_date']
                ).dt.days
                mediana_transp = df_merged['velocidade_transportadora_dias'].median()
                df_merged['velocidade_transportadora_dias'] = df_merged['velocidade_transportadora_dias'].fillna(mediana_transp)

            # Feature 8: compra_fds (sexta-domingo)
            df_merged['compra_fds'] = (df_merged['dia_semana_compra'] >= 5).astype(int)

            # Feature 9: mes_compra (1-12)
            df_merged['mes_compra'] = df_merged['order_purchase_timestamp'].dt.month

            # Feature 10: valor_total_pedido
            df_merged['valor_total_pedido'] = df_merged['price'] + df_merged['freight_value']

            # Feature 11: destino_tipo (Capital/Interior)
            capitais = [
                'rio branco', 'maceio', 'macapa', 'manaus', 'salvador', 'fortaleza', 'brasilia', 'vitoria',
                'goiania', 'sao luis', 'cuiaba', 'campo grande', 'belo horizonte', 'belem', 'joao pessoa',
                'curitiba', 'recife', 'teresina', 'rio de janeiro', 'natal', 'porto alegre', 'porto velho',
                'boa vista', 'florianopolis', 'sao paulo', 'aracaju', 'palmas'
            ]
            if 'customer_city' in df_merged.columns:
                df_merged['destino_tipo'] = np.where(
                    df_merged['customer_city'].str.lower().isin(capitais),
                    'Capital',
                    'Interior'
                )

            # Feature 12: volume_cm3 (se não existir)
            if 'volume_cm3' not in df_merged.columns:
                if all(col in df_merged.columns for col in ['product_length_cm', 'product_height_cm', 'product_width_cm']):
                    df_merged['volume_cm3'] = (
                        df_merged['product_length_cm'] *
                        df_merged['product_height_cm'] *
                        df_merged['product_width_cm']
                    )

            logger.info("15 features derivadas criadas conforme notebook")

            # DROPNA FINAL (conforme notebook - limpeza agressiva)
            linhas_antes_dropna = len(df_merged)
            df_merged = df_merged.dropna()
            linhas_dropadas = linhas_antes_dropna - len(df_merged)
            logger.info(f"Dropna final: {linhas_dropadas} linhas removidas ({linhas_antes_dropna} -> {len(df_merged)})")

            self._data = df_merged
            logger.info(f"Dados históricos carregados: {len(self._data)} linhas (Merged c/ Clientes, Produtos, Sellers, Payments e Geo)")
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
            geo_raw = pd.read_csv(geo_file)

            # Deduplicar por CEP (conforme notebook)
            self._geolocation = (
                geo_raw
                .groupby('geolocation_zip_code_prefix', as_index=False)
                .agg({'geolocation_lat': 'mean', 'geolocation_lng': 'mean'})
            )
            logger.info(f"Geolocalização carregada e deduplicada: {len(geo_raw)} -> {len(self._geolocation)} CEPs únicos")
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
