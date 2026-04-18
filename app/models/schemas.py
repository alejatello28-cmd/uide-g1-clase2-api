from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CoinPrice(BaseModel):
    id: str = Field(..., description="ID único de la criptomoneda")
    symbol: str = Field(..., description="Símbolo (ej: btc, eth)")
    name: str = Field(..., description="Nombre completo")
    current_price: Optional[float] = Field(None, description="Precio actual en USD")
    market_cap: Optional[float] = Field(None, description="Capitalización de mercado")
    market_cap_rank: Optional[int] = Field(None, description="Ranking por market cap")
    total_volume: Optional[float] = Field(None, description="Volumen de trading 24h")
    price_change_24h: Optional[float] = Field(None, description="Cambio de precio en 24h")
    price_change_percentage_24h: Optional[float] = Field(None, description="% cambio en 24h")
    price_change_percentage_7d: Optional[float] = Field(None, description="% cambio en 7 días")
    circulating_supply: Optional[float] = Field(None, description="Suministro circulante")
    ath: Optional[float] = Field(None, description="All-time high")
    ath_date: Optional[str] = Field(None, description="Fecha del ATH")
    last_updated: Optional[str] = Field(None, description="Última actualización")
    image: Optional[str] = Field(None, description="URL del logo")

    class Config:
        from_attributes = True


class CoinSimple(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    market_cap: Optional[float] = None
    image: Optional[str] = None


class ConversionResult(BaseModel):
    from_coin: str = Field(..., description="Moneda origen")
    to_currency: str = Field(..., description="Moneda destino")
    amount: float = Field(..., description="Cantidad convertida")
    rate: float = Field(..., description="Tasa de cambio")
    result: float = Field(..., description="Resultado de la conversión")
    timestamp: str = Field(..., description="Timestamp de la conversión")


class HistoricalPrice(BaseModel):
    timestamp: str
    price: float
    market_cap: float
    total_volume: float


class TrendingCoin(BaseModel):
    id: str
    name: str
    symbol: str
    market_cap_rank: Optional[int] = None
    price_btc: Optional[float] = None
    score: Optional[int] = None


class MarketOverview(BaseModel):
    active_cryptocurrencies: int
    total_market_cap_usd: float
    total_volume_usd: float
    market_cap_percentage_btc: float
    market_cap_percentage_eth: float
    market_cap_change_percentage_24h: float


class APIResponse(BaseModel):
    success: bool = True
    data: object
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
