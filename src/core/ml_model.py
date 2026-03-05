"""
Carregamento e gerenciamento do modelo XGBoost
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Optional
from src.config import MODEL_PATH
from src.utils.logger import get_logger
from src.utils.exceptions import ModelNotLoadedException, PredictionException

logger = get_logger(__name__)


class MLModelLoader:
    """
    Singleton para carregar e cachear o modelo XGBoost em memória
    """
    _instance: Optional['MLModelLoader'] = None
    _model: Optional[any] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_path: Optional[str] = None) -> any:
        """
        Carrega o modelo .pkl do disco (apenas na primeira vez)

        Args:
            model_path: Caminho para o arquivo .pkl do modelo (opcional)

        Returns:
            Modelo XGBoost carregado

        Raises:
            FileNotFoundError: Se o arquivo do modelo não existir
            ModelNotLoadedException: Se o modelo não puder ser carregado
        """
        if self._model is not None:
            logger.info("Modelo já carregado em memória")
            return self._model

        path = model_path or MODEL_PATH
        model_file = Path(path)

        if not model_file.exists():
            logger.error(f"Modelo não encontrado em: {model_file}")
            raise FileNotFoundError(
                f"Modelo não encontrado: {model_file}. "
                f"Por favor, treine o modelo e salve em {MODEL_PATH}"
            )

        try:
            logger.info(f"Carregando modelo de: {model_file}")
            self._model = joblib.load(model_file)
            logger.info("Modelo carregado com sucesso")
            return self._model
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            raise ModelNotLoadedException(f"Erro ao carregar modelo: {str(e)}")

    def predict_proba(self, features_array: np.ndarray) -> float:
        """
        Realiza predição e retorna probabilidade de atraso

        Args:
            features_array: Array numpy com as features processadas

        Returns:
            Probabilidade da classe 1 (atraso) entre 0 e 1

        Raises:
            ModelNotLoadedException: Se o modelo não estiver carregado
            PredictionException: Se houver erro na predição
        """
        if self._model is None:
            logger.error("Tentativa de predição sem modelo carregado")
            raise ModelNotLoadedException(
                "Modelo não carregado. Execute load_model() primeiro"
            )

        try:
            # Predição de probabilidades
            proba = self._model.predict_proba(features_array)
            # Retorna probabilidade da classe positiva (atraso)
            prob_atraso = proba[0][1]
            logger.debug(f"Probabilidade de atraso: {prob_atraso:.4f}")
            return float(prob_atraso)
        except Exception as e:
            logger.error(f"Erro ao realizar predição: {str(e)}")
            raise PredictionException(f"Erro ao realizar predição: {str(e)}")

    def is_loaded(self) -> bool:
        """
        Verifica se o modelo está carregado

        Returns:
            True se o modelo está carregado, False caso contrário
        """
        return self._model is not None


# Singleton global
ml_model = MLModelLoader()
