"""
Servicio de integración con CoinGecko API
Documentación: https://www.coingecko.com/en/api/documentation
"""

import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.config import settings


class CoinGeckoService:
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "CryptoAPI/1.0.0",
        }

    async def _get(self, endpoint: str, params: Dict = None) -> Any:
        """Realiza una petición GET a CoinGecko."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_markets(
        self,
        vs_currency: str = "usd",
        per_page: int = 20,
        page: int = 1,
        order: str = "market_cap_desc",
        ids: Optional[str] = None,
    ) -> List[Dict]:
        """Obtiene lista de criptomonedas con datos de mercado."""
        params = {
            "vs_currency": vs_currency,
            "per_page": min(per_page, 250),
            "page": page,
            "order": order,
            "sparkline": False,
            "price_change_percentage": "24h,7d",
        }
        if ids:
            params["ids"] = ids

        data = await self._get("/coins/markets", params)
        return data

    async def get_coin_detail(self, coin_id: str) -> Dict:
        """Obtiene detalle completo de una criptomoneda."""
        params = {
            "localization": False,
            "tickers": False,
            "market_data": True,
            "community_data": False,
            "developer_data": False,
        }
        return await self._get(f"/coins/{coin_id}", params)

    async def get_price(
        self, ids: str, vs_currencies: str = "usd"
    ) -> Dict:
        """Obtiene precios simples de una o varias criptomonedas."""
        params = {
            "ids": ids,
            "vs_currencies": vs_currencies,
            "include_24hr_change": True,
            "include_market_cap": True,
            "include_24hr_vol": True,
        }
        return await self._get("/simple/price", params)

    async def get_coin_history(
        self, coin_id: str, days: int = 7, vs_currency: str = "usd"
    ) -> Dict:
        """Obtiene historial de precios de una criptomoneda."""
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily" if days > 1 else "hourly",
        }
        return await self._get(f"/coins/{coin_id}/market_chart", params)

    async def get_trending(self) -> Dict:
        """Obtiene criptomonedas en tendencia (top 7 búsquedas en 24h)."""
        return await self._get("/search/trending")

    async def get_global(self) -> Dict:
        """Obtiene datos globales del mercado cripto."""
        return await self._get("/global")

    async def search_coins(self, query: str) -> Dict:
        """Busca criptomonedas por nombre o símbolo."""
        return await self._get("/search", {"query": query})

    async def get_supported_currencies(self) -> List[str]:
        """Obtiene lista de monedas fiat soportadas."""
        return await self._get("/simple/supported_vs_currencies")

    async def get_exchanges(self, per_page: int = 10) -> List[Dict]:
        """Obtiene lista de exchanges por volumen."""
        return await self._get("/exchanges", {"per_page": per_page})


# Instancia singleton del servicio
coingecko = CoinGeckoService()
