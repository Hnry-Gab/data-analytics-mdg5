"""
Exceções customizadas para a aplicação
"""


class OlistAPIException(Exception):
    """Exceção base para a API Olist"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ModelNotLoadedException(OlistAPIException):
    """Exceção quando o modelo ML não está carregado"""
    def __init__(self, message: str = "Modelo de ML não está carregado"):
        super().__init__(message, status_code=503)


class DataNotLoadedException(OlistAPIException):
    """Exceção quando os dados não estão carregados"""
    def __init__(self, message: str = "Dados não estão carregados"):
        super().__init__(message, status_code=503)


class InvalidFeatureException(OlistAPIException):
    """Exceção quando as features de entrada são inválidas"""
    def __init__(self, message: str = "Features de entrada inválidas"):
        super().__init__(message, status_code=400)


class PredictionException(OlistAPIException):
    """Exceção durante o processo de predição"""
    def __init__(self, message: str = "Erro ao realizar predição"):
        super().__init__(message, status_code=500)


class CEPNotFoundException(OlistAPIException):
    """Exceção quando CEP não é encontrado na base de geolocalização"""
    def __init__(self, message: str = "CEP não encontrado"):
        super().__init__(message, status_code=404)
