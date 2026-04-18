"""
CryptoAPI v1 - Endpoints principales
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import httpx

from app.services.coingecko import coingecko

router = APIRouter()


# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@router.get("/health", tags=["Sistema"], summary="Estado del API")
async def health_check():
    """Verifica que el API esté funcionando correctamente."""
    try:
        # Ping a CoinGecko
        await coingecko._get("/ping")
        coingecko_status = "online"
    except Exception:
        coingecko_status = "offline"

    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "online",
            "coingecko": coingecko_status,
        },
    }


# ─────────────────────────────────────────────
# MERCADOS
# ─────────────────────────────────────────────

@router.get("/markets", tags=["Mercados"], summary="Top criptomonedas con datos de mercado")
async def get_markets(
    currency: str = Query("usd", description="Moneda de referencia (usd, eur, btc, etc.)"),
    per_page: int = Query(20, ge=1, le=100, description="Resultados por página"),
    page: int = Query(1, ge=1, description="Número de página"),
    order: str = Query(
        "market_cap_desc",
        description="Orden: market_cap_desc, volume_desc, gecko_desc, price_asc, price_desc",
    ),
):
    """
    Retorna lista de criptomonedas ordenadas con datos completos de mercado:
    precio, market cap, volumen, variaciones de precio, etc.
    """
    try:
        data = await coingecko.get_markets(
            vs_currency=currency, per_page=per_page, page=page, order=order
        )
        return {
            "success": True,
            "currency": currency,
            "page": page,
            "per_page": per_page,
            "count": len(data),
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener mercados: {str(e)}")


# ─────────────────────────────────────────────
# PRECIOS
# ─────────────────────────────────────────────

@router.get("/coins/price", tags=["Precios"], summary="Precio(s) simple(s) de criptomonedas")
async def get_price(
    ids: str = Query(
        ...,
        description="IDs separados por coma. Ej: bitcoin,ethereum,solana",
        example="bitcoin,ethereum,solana",
    ),
    currencies: str = Query(
        "usd",
        description="Monedas separadas por coma. Ej: usd,eur,btc",
        example="usd,eur",
    ),
):
    """
    Obtiene el precio actual de una o varias criptomonedas en una o varias monedas.
    Incluye cambio 24h, market cap y volumen.
    """
    try:
        data = await coingecko.get_price(ids=ids, vs_currencies=currencies)
        if not data:
            raise HTTPException(status_code=404, detail="No se encontraron las criptomonedas especificadas")
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# DETALLE DE MONEDA
# ─────────────────────────────────────────────

@router.get("/coins/{coin_id}", tags=["Monedas"], summary="Detalle completo de una criptomoneda")
async def get_coin_detail(
    coin_id: str,
):
    """
    Retorna información completa de una criptomoneda: descripción, links,
    datos de mercado, rankings, ATH, ATL, etc.
    """
    try:
        data = await coingecko.get_coin_detail(coin_id)
        market = data.get("market_data", {})
        return {
            "success": True,
            "data": {
                "id": data.get("id"),
                "symbol": data.get("symbol"),
                "name": data.get("name"),
                "description": data.get("description", {}).get("en", "")[:500],
                "image": data.get("image", {}).get("large"),
                "categories": data.get("categories", []),
                "homepage": data.get("links", {}).get("homepage", [None])[0],
                "genesis_date": data.get("genesis_date"),
                "market_cap_rank": data.get("market_cap_rank"),
                "coingecko_score": data.get("coingecko_score"),
                "market_data": {
                    "current_price_usd": market.get("current_price", {}).get("usd"),
                    "market_cap_usd": market.get("market_cap", {}).get("usd"),
                    "total_volume_usd": market.get("total_volume", {}).get("usd"),
                    "price_change_24h": market.get("price_change_24h"),
                    "price_change_percentage_24h": market.get("price_change_percentage_24h"),
                    "price_change_percentage_7d": market.get("price_change_percentage_7d"),
                    "price_change_percentage_30d": market.get("price_change_percentage_30d"),
                    "ath_usd": market.get("ath", {}).get("usd"),
                    "ath_date": market.get("ath_date", {}).get("usd"),
                    "atl_usd": market.get("atl", {}).get("usd"),
                    "circulating_supply": market.get("circulating_supply"),
                    "max_supply": market.get("max_supply"),
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Criptomoneda '{coin_id}' no encontrada")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# HISTORIAL
# ─────────────────────────────────────────────

@router.get("/coins/{coin_id}/history", tags=["Historial"], summary="Historial de precios")
async def get_history(
    coin_id: str,
    days: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    currency: str = Query("usd", description="Moneda de referencia"),
):
    """
    Retorna el historial de precios, market cap y volumen de una criptomoneda
    para los últimos N días.
    """
    try:
        raw = await coingecko.get_coin_history(coin_id=coin_id, days=days, vs_currency=currency)

        prices = raw.get("prices", [])
        market_caps = raw.get("market_caps", [])
        volumes = raw.get("total_volumes", [])

        history = []
        for i, price_point in enumerate(prices):
            ts_ms, price = price_point
            ts = datetime.utcfromtimestamp(ts_ms / 1000).isoformat()
            entry = {
                "timestamp": ts,
                "price": round(price, 6),
            }
            if i < len(market_caps):
                entry["market_cap"] = round(market_caps[i][1], 2)
            if i < len(volumes):
                entry["volume"] = round(volumes[i][1], 2)
            history.append(entry)

        # Stats del período
        prices_only = [p["price"] for p in history]
        stats = {}
        if prices_only:
            stats = {
                "min_price": min(prices_only),
                "max_price": max(prices_only),
                "avg_price": round(sum(prices_only) / len(prices_only), 6),
                "price_change": round(prices_only[-1] - prices_only[0], 6),
                "price_change_pct": round(
                    ((prices_only[-1] - prices_only[0]) / prices_only[0]) * 100, 2
                ) if prices_only[0] != 0 else 0,
            }

        return {
            "success": True,
            "coin_id": coin_id,
            "currency": currency,
            "days": days,
            "data_points": len(history),
            "stats": stats,
            "history": history,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Criptomoneda '{coin_id}' no encontrada")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# TRENDING
# ─────────────────────────────────────────────

@router.get("/trending", tags=["Tendencias"], summary="Criptomonedas en tendencia")
async def get_trending():
    """
    Retorna las 7 criptomonedas más buscadas en las últimas 24 horas
    según CoinGecko.
    """
    try:
        data = await coingecko.get_trending()
        coins = data.get("coins", [])

        result = []
        for item in coins:
            coin = item.get("item", {})
            result.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "price_btc": coin.get("price_btc"),
                "score": coin.get("score"),
                "thumb": coin.get("thumb"),
            })

        return {
            "success": True,
            "count": len(result),
            "data": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# CONVERSIÓN
# ─────────────────────────────────────────────

@router.get("/convert", tags=["Conversión"], summary="Convertir entre cripto y fiat")
async def convert(
    from_coin: str = Query(..., description="ID de la moneda origen. Ej: bitcoin", example="bitcoin"),
    to_currency: str = Query("usd", description="Moneda destino. Ej: usd, eur, eth", example="usd"),
    amount: float = Query(1.0, ge=0, description="Cantidad a convertir"),
):
    """
    Convierte una cantidad de criptomoneda a otra moneda (fiat o crypto).
    Ejemplo: ¿Cuántos USD equivalen a 2.5 Bitcoin?
    """
    try:
        data = await coingecko.get_price(ids=from_coin, vs_currencies=to_currency)

        if from_coin not in data:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró la criptomoneda '{from_coin}'",
            )

        rate = data[from_coin].get(to_currency)
        if rate is None:
            raise HTTPException(
                status_code=400,
                detail=f"Moneda destino '{to_currency}' no soportada",
            )

        result = amount * rate

        return {
            "success": True,
            "data": {
                "from_coin": from_coin,
                "to_currency": to_currency,
                "amount": amount,
                "rate": rate,
                "result": result,
                "formatted": f"{amount} {from_coin.upper()} = {result:,.6f} {to_currency.upper()}",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# GLOBAL
# ─────────────────────────────────────────────

@router.get("/global", tags=["Mercados"], summary="Resumen global del mercado cripto")
async def get_global_market():
    """
    Retorna estadísticas globales del mercado de criptomonedas:
    total de activos, capitalización total, volumen, dominancia BTC/ETH.
    """
    try:
        raw = await coingecko.get_global()
        data = raw.get("data", {})

        return {
            "success": True,
            "data": {
                "active_cryptocurrencies": data.get("active_cryptocurrencies"),
                "markets": data.get("markets"),
                "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
                "total_volume_usd": data.get("total_volume", {}).get("usd"),
                "market_cap_percentage": {
                    "btc": round(data.get("market_cap_percentage", {}).get("btc", 0), 2),
                    "eth": round(data.get("market_cap_percentage", {}).get("eth", 0), 2),
                },
                "market_cap_change_percentage_24h_usd": data.get(
                    "market_cap_change_percentage_24h_usd"
                ),
                "updated_at": data.get("updated_at"),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# BÚSQUEDA
# ─────────────────────────────────────────────

@router.get("/search", tags=["Búsqueda"], summary="Buscar criptomonedas")
async def search_coins(
    q: str = Query(..., min_length=2, description="Término de búsqueda", example="solana"),
):
    """
    Busca criptomonedas por nombre o símbolo.
    Retorna lista de resultados con ID, nombre, símbolo y ranking.
    """
    try:
        data = await coingecko.search_coins(query=q)
        coins = data.get("coins", [])[:15]  # máx 15 resultados

        return {
            "success": True,
            "query": q,
            "count": len(coins),
            "data": coins,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# EXCHANGES
# ─────────────────────────────────────────────

@router.get("/exchanges", tags=["Exchanges"], summary="Top exchanges por volumen")
async def get_exchanges(
    limit: int = Query(10, ge=1, le=50, description="Número de exchanges a retornar"),
):
    """
    Retorna los principales exchanges de criptomonedas ordenados por volumen de trading.
    """
    try:
        data = await coingecko.get_exchanges(per_page=limit)
        result = [
            {
                "id": ex.get("id"),
                "name": ex.get("name"),
                "country": ex.get("country"),
                "url": ex.get("url"),
                "trust_score": ex.get("trust_score"),
                "trade_volume_24h_btc": ex.get("trade_volume_24h_btc"),
                "year_established": ex.get("year_established"),
                "image": ex.get("image"),
            }
            for ex in data
        ]
        return {
            "success": True,
            "count": len(result),
            "data": result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
