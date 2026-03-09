"""
Schemas Pydantic para validação de dados de entrada e saída (V5 CatBoost)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime

class PedidoInput(BaseModel):
    """
    Dados de entrada brutos para predição de atraso logístico V5
    """
    # Dados de Localidade e Categoria (Textuais Nativas)
    cep_cliente: str = Field(..., description="CEP do destinatário (8 dígitos)", min_length=8, max_length=8, pattern=r'^\d{8}$')
    cep_vendedor: str = Field(..., description="CEP do remetente (8 dígitos)", min_length=8, max_length=8, pattern=r'^\d{8}$')
    categoria_produto: str = Field(..., description="Nome da categoria (ex: 'beleza_saude')", min_length=1)
    
    # Dados Dimensionais e Preço
    peso_produto_g: float = Field(..., gt=0, description="Peso em gramas", example=1500.0)
    preco_produto: float = Field(..., gt=0, description="Valor do produto em reais", example=149.90)
    preco_frete: float = Field(..., gt=0, description="Valor do frete em reais", example=25.00)
    volume_cm3: float = Field(..., gt=0, description="Volume da caixa em cm³", example=3500.0)
    total_itens_pedido: int = Field(1, ge=1, description="Qtd de itens neste pacote", example=1)
    
    # Dados de Prazos (SLA)
    prazo_estimado_dias: int = Field(..., ge=1, description="SLA prometido ao cliente (Dias para entrega)", example=15)
    
    # Dados do Vendedor (Históricos Simulados/Reais)
    velocidade_lojista_dias: float = Field(..., ge=0, description="Média de dias que o lojista leva para postar no correio", example=2.5)
    historico_atraso_vendedor: float = Field(..., ge=0, description="Taxa de atraso histórica do lojista (0.0 a 1.0)", example=0.08)
    qtd_pedidos_anteriores_vendedor: int = Field(..., ge=0, description="Volumetria total do lojista", example=45)
    
    # Contexto Temporal
    data_aprovacao: str = Field(..., description="Data/Hora da compra (ISO 8601)", example="2018-02-15T14:30:00")

    @field_validator('cep_cliente', 'cep_vendedor')
    @classmethod
    def validate_cep(cls, v: str) -> str:
        if not v.isdigit(): raise ValueError('CEP deve conter apenas dígitos')
        if len(v) != 8: raise ValueError('CEP deve ter exactly 8 dígitos')
        return v

    @field_validator('categoria_produto')
    @classmethod
    def validate_categoria(cls, v: str) -> str:
        # Converter hifens ou espaços pra underline p/ seguir padrão Olist
        return v.lower().strip().replace(" ", "_").replace("-", "_")

    class Config:
        json_schema_extra = {
            "example": {
                "cep_cliente": "01310100",
                "cep_vendedor": "20040020",
                "categoria_produto": "perfumaria",
                "peso_produto_g": 500.0,
                "preco_produto": 99.90,
                "preco_frete": 15.00,
                "volume_cm3": 8000.0,
                "total_itens_pedido": 1,
                "prazo_estimado_dias": 12,
                "velocidade_lojista_dias": 1.5,
                "historico_atraso_vendedor": 0.0,
                "qtd_pedidos_anteriores_vendedor": 100,
                "data_aprovacao": "2018-11-23T10:00:00"
            }
        }

class PredictionOutput(BaseModel):
    """Resposta interativa de ML"""
    probabilidade_atraso: float = Field(..., ge=0, le=100)
    classe_predicao: str = Field(..., description="'No Prazo' ou 'Atrasado'")
    confianca: float = Field(..., ge=0, le=100)
    limiar_corte: float = Field(..., description="Threshold dinâmico usado")
    features_utilizadas: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    data_loaded: bool

class FeaturesResponse(BaseModel):
    features: list[str]
    description: str
