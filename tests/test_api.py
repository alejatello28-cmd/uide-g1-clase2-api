"""
Tests para CryptoAPI v1
Ejecutar con: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)


# ─────────────────────────────────────────────
# Tests básicos
# ─────────────────────────────────────────────

def test_root():
    """El endpoint raíz retorna información del API."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert "endpoints" in data


def test_health():
    """El health check del API funciona."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ─────────────────────────────────────────────
# Tests de endpoints con mock
# ─────────────────────────────────────────────

MOCK_MARKETS = [
    {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 95000.0,
        "market_cap": 1880000000000,
        "market_cap_rank": 1,
        "total_volume": 45000000000,
        "price_change_24h": 1500.0,
        "price_change_percentage_24h": 1.6,
        "price_change_percentage_7d_in_currency": 5.2,
        "circulating_supply": 19800000,
        "ath": 108000,
        "ath_date": "2024-12-17",
        "last_updated": "2025-01-01T00:00:00Z",
        "image": "https://example.com/btc.png",
    }
]


@patch("app.api.v1.endpoints.crypto.coingecko")
def test_get_markets(mock_cg):
    """El endpoint /markets retorna datos de mercado."""
    mock_cg.get_markets = AsyncMock(return_value=MOCK_MARKETS)

    response = client.get("/api/v1/markets")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["data"][0]["id"] == "bitcoin"


@patch("app.api.v1.endpoints.crypto.coingecko")
def test_get_price(mock_cg):
    """El endpoint /coins/price retorna precios correctamente."""
    mock_cg.get_price = AsyncMock(
        return_value={"bitcoin": {"usd": 95000, "usd_24h_change": 1.6}}
    )

    response = client.get("/api/v1/coins/price?ids=bitcoin")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "bitcoin" in data["data"]


@patch("app.api.v1.endpoints.crypto.coingecko")
def test_get_trending(mock_cg):
    """El endpoint /trending retorna monedas en tendencia."""
    mock_cg.get_trending = AsyncMock(
        return_value={
            "coins": [
                {
                    "item": {
                        "id": "solana",
                        "name": "Solana",
                        "symbol": "SOL",
                        "market_cap_rank": 5,
                        "price_btc": 0.002,
                        "score": 0,
                        "thumb": "https://example.com/sol.png",
                    }
                }
            ]
        }
    )

    response = client.get("/api/v1/trending")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == "solana"


@patch("app.api.v1.endpoints.crypto.coingecko")
def test_convert(mock_cg):
    """El endpoint /convert calcula conversión correctamente."""
    mock_cg.get_price = AsyncMock(
        return_value={"bitcoin": {"usd": 95000.0}}
    )

    response = client.get("/api/v1/convert?from_coin=bitcoin&to_currency=usd&amount=2")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["result"] == 190000.0
    assert data["data"]["rate"] == 95000.0


@patch("app.api.v1.endpoints.crypto.coingecko")
def test_search(mock_cg):
    """El endpoint /search retorna resultados de búsqueda."""
    mock_cg.search_coins = AsyncMock(
        return_value={
            "coins": [
                {"id": "solana", "name": "Solana", "symbol": "SOL", "market_cap_rank": 5}
            ]
        }
    )

    response = client.get("/api/v1/search?q=solana")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query"] == "solana"


def test_search_too_short():
    """Búsqueda con menos de 2 caracteres retorna 422."""
    response = client.get("/api/v1/search?q=a")
    assert response.status_code == 422


@patch("app.api.v1.endpoints.crypto.coingecko")
def test_convert_invalid_coin(mock_cg):
    """Conversión con moneda inválida retorna 404."""
    mock_cg.get_price = AsyncMock(return_value={})

    response = client.get("/api/v1/convert?from_coin=fakecoin&to_currency=usd")
    assert response.status_code == 404
