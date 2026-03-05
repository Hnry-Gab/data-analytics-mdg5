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
        """
        Carrega CSV com dados processados (apenas na primeira vez)

        Args:
            csv_path: Caminho para o CSV processado (opcional)

        Returns:
            DataFrame com dados históricos

        Raises:
            FileNotFoundError: Se o arquivo CSV não existir
            DataNotLoadedException: Se os dados não puderem ser carregados
        """
        if self._data is not None:
            logger.info("Dados já carregados em memória")
            return self._data

        path = csv_path or CSV_PATH
        csv_file = Path(path)

        if not csv_file.exists():
            logger.warning(
                f"CSV não encontrado em: {csv_file}. "
                f"Algumas funcionalidades podem não estar disponíveis."
            )
            # Não lançar exceção, pois os dados históricos são opcionais
            return pd.DataFrame()

        try:
            logger.info(f"Carregando dados de: {csv_file}")
            self._data = pd.read_csv(csv_file)
            logger.info(f"Dados carregados: {len(self._data)} linhas")
            return self._data
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            raise DataNotLoadedException(f"Erro ao carregar dados: {str(e)}")

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
            csv_dir = Path(CSV_PATH).parent
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
