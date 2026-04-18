"""
CryptoAPI - Real-time Cryptocurrency & Financial Data API
Built with FastAPI | v1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="💰 CryptoAPI",
    description="""
## CryptoAPI - API de Datos Financieros en Tiempo Real

Una API RESTful construida con **FastAPI** que provee datos de criptomonedas
y mercados financieros en tiempo real integrando la API pública de CoinGecko.

### Funcionalidades
- 📈 Precios en tiempo real de criptomonedas
- 📊 Estadísticas de mercado (market cap, volumen, variaciones)
- 🔝 Top criptomonedas por capitalización de mercado
- 💱 Conversión entre criptomonedas y monedas fiat
- 📉 Datos históricos de precios
- 🔍 Búsqueda de activos

### Versiones
- **v1** → Versión estable actual
    """,
    version="1.0.0",
    contact={
        "name": "CryptoAPI Team",
        "url": "https://github.com/tu-usuario/crypto-api",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"], summary="Bienvenida al API")
async def root():
    return {
        "message": "💰 Bienvenido a CryptoAPI",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "v1": "/api/v1",
            "health": "/api/v1/health",
            "coins": "/api/v1/coins",
            "markets": "/api/v1/markets",
            "trending": "/api/v1/trending",
            "convert": "/api/v1/convert",
            "history": "/api/v1/coins/{id}/history",
        },
    }


@app.get("/health", tags=["Root"], summary="Health check general")
async def health():
    return {"status": "ok", "service": "CryptoAPI"}
