"""
Carregamento e gerenciamento do modelo CatBoost V5
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from catboost import CatBoostClassifier
import numpy as np
import pandas as pd

from src.config import MODEL_PATH, MODEL_CONFIG_PATH
from src.utils.logger import get_logger
from src.utils.exceptions import ModelNotLoadedException, PredictionException

logger = get_logger(__name__)

class MLModelLoader:
    """
    Singleton para carregar e cachear o modelo CatBoost em memória
    """
    _instance: Optional['MLModelLoader'] = None
    _model: Optional[CatBoostClassifier] = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_path: Optional[str] = None, config_path: Optional[str] = None) -> CatBoostClassifier:
        """
        Carrega o modelo nativo abstrato .cbm e suas métricas otimizadas do JSON
        """
        if self._model is not None and self._config is not None:
            logger.info("Modelo CatBoost e Configuração já carregados em memória")
            return self._model

        path = model_path or MODEL_PATH
        model_file = Path(path)
        conf_path = config_path or MODEL_CONFIG_PATH
        conf_file = Path(conf_path)

        if not model_file.exists() or not conf_file.exists():
            raise FileNotFoundError(
                f"Archivos do Modelo v5 não encontrados: {model_file} ou {conf_file}. "
                f"Treine e garanta exportação de .cbm e .json na pasta v5."
            )

        try:
            # 1. Carrega hiperparametros e threshold
            logger.info(f"Carregando JSON de configurações em: {conf_file}")
            with open(conf_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)

            # 2. Carrega motor em C++ Nativo (muito mais leve/rápido que pickle)
            logger.info(f"Carregando modelo executável em: {model_file}")
            self._model = CatBoostClassifier()
            self._model.load_model(str(model_file))

            logger.info(f"✓ CatBoost (treinado c/ threshold de {self._config.get('threshold', 0.5):.2f}) e {self._config.get('n_features')} features ativado!")
            return self._model

        except Exception as e:
            logger.error(f"Erro ao inicializar CatBoost v5: {str(e)}")
            raise ModelNotLoadedException(f"Erro ao carregar modelo: {str(e)}")

    def predict_proba(self, features_df: pd.DataFrame) -> tuple[float, float, str]:
        """
        Prediz risco de atraso operando no limiar dinâmico achado no grid search.
        
        Retorna:
            Probabilidade (0 a 1)
            Confiança Matemática
            Classe (Atrasado, No Prazo)
        """
        if self._model is None or self._config is None:
            raise ModelNotLoadedException("Modelo não inicializado executado no endpoint.")

        try:
            # Extrair o ponto de virada exato mapeado pelo cientista de dados
            thresh = self._config.get('threshold', 0.5)
            
            # Predict Proba entrega array tipo [Prob_Classe0, Prob_Classe1]
            probas = self._model.predict_proba(features_df)
            prob_atraso = float(probas[0][1])
            
            classe = "Atrasado" if prob_atraso >= thresh else "No Prazo"
            confianca_bruta = prob_atraso if prob_atraso >= thresh else (1.0 - prob_atraso)
            
            logger.debug(f">> Ticker ML: Prob={prob_atraso:.2f} | T={thresh:.2f} => {classe.upper()}")
            
            return prob_atraso, float(confianca_bruta), classe

        except Exception as e:
            logger.error(f"Engine de Previsão CatBoost Crashou: {str(e)}")
            raise PredictionException(f"Erro crasso na predição MLEngine: {str(e)}")

    def is_loaded(self) -> bool:
        return self._model is not None and self._config is not None

# Singleton global do Motor V5
ml_model = MLModelLoader()
