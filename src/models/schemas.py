"""
Schemas Pydantic para validação de dados de entrada e saída
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any


class PedidoInput(BaseModel):
    """
    Dados de entrada para predição de atraso logístico
    """
    cep_cliente: str = Field(
        ...,
        description="CEP do cliente (8 dígitos)",
        min_length=8,
        max_length=8,
        pattern=r'^\d{8}$'
    )
    cep_vendedor: str = Field(
        ...,
        description="CEP do vendedor (8 dígitos)",
        min_length=8,
        max_length=8,
        pattern=r'^\d{8}$'
    )
    categoria_produto: str = Field(
        ...,
        description="Categoria do produto (ex: eletronicos, moda, casa)",
        min_length=1
    )
    peso_produto_kg: float = Field(
        ...,
        gt=0,
        description="Peso do produto em quilogramas",
        example=2.5
    )
    preco_frete: float = Field(
        ...,
        gt=0,
        description="Preço do frete em reais",
        example=15.00
    )
    peso_produto_volume_cm3: float = Field(
        ...,
        gt=0,
        description="Volume do produto em cm³",
        example=5000.0
    )

    @field_validator('cep_cliente', 'cep_vendedor')
    @classmethod
    def validate_cep(cls, v: str) -> str:
        """Valida formato do CEP"""
        if not v.isdigit():
            raise ValueError('CEP deve conter apenas dígitos')
        if len(v) != 8:
            raise ValueError('CEP deve ter exatamente 8 dígitos')
        return v

    @field_validator('categoria_produto')
    @classmethod
    def validate_categoria(cls, v: str) -> str:
        """Normaliza categoria do produto"""
        return v.lower().strip()

    class Config:
        json_schema_extra = {
            "example": {
                "cep_cliente": "01310100",
                "cep_vendedor": "20040020",
                "categoria_produto": "eletronicos",
                "peso_produto_kg": 2.5,
                "preco_frete": 15.00,
                "peso_produto_volume_cm3": 5000.0
            }
        }


class PredictionOutput(BaseModel):
    """
    Resposta da predição de atraso
    """
    probabilidade_atraso: float = Field(
        ...,
        ge=0,
        le=100,
        description="Probabilidade de atraso em porcentagem (0-100%)"
    )
    classe_predicao: str = Field(
        ...,
        description="Classificação: 'No Prazo' ou 'Atrasado'"
    )
    confianca: float = Field(
        ...,
        ge=0,
        le=100,
        description="Confiança da predição em porcentagem (0-100%)"
    )
    features_utilizadas: Dict[str, Any] = Field(
        ...,
        description="Features processadas e utilizadas na predição"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "probabilidade_atraso": 23.45,
                "classe_predicao": "No Prazo",
                "confianca": 76.55,
                "features_utilizadas": {
                    "distancia_km": 450.5,
                    "categoria_encoded": 3,
                    "peso_kg": 2.5,
                    "preco_frete": 15.00
                }
            }
        }


class HealthResponse(BaseModel):
    """
    Resposta do endpoint de health check
    """
    status: str = Field(..., description="Status da aplicação")
    model_loaded: bool = Field(..., description="Se o modelo ML está carregado")
    data_loaded: bool = Field(..., description="Se os dados estão carregados")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "data_loaded": True
            }
        }


class FeaturesResponse(BaseModel):
    """
    Lista de features aceitas pela API
    """
    features: list[str] = Field(..., description="Lista de features de entrada")
    description: str = Field(..., description="Descrição das features")

    class Config:
        json_schema_extra = {
            "example": {
                "features": [
                    "cep_cliente",
                    "cep_vendedor",
                    "categoria_produto",
                    "peso_produto_kg",
                    "preco_frete",
                    "peso_produto_volume_cm3"
                ],
                "description": "Features necessárias para predição de atraso"
            }
        }
