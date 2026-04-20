# 💰 CryptoAPI — API de Datos Financieros en Tiempo Real

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-9%20passed-brightgreen?style=flat&logo=pytest)](./tests)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

API RESTful construida con **FastAPI** que provee datos de criptomonedas y mercados financieros en **tiempo real**, integrando la API pública de **CoinGecko**.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Endpoints](#-endpoints)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Screenshots](#-screenshots)
- [Tests](#-tests)
- [Tecnologías](#-tecnologías)

---

## ✨ Características

| Funcionalidad | Descripción |
|---|---|
| 📈 Precios en tiempo real | Datos actualizados de cualquier criptomoneda |
| 📊 Datos de mercado | Market cap, volumen, variaciones 1h/24h/7d/30d |
| 🔝 Top 100 | Lista completa de criptos por capitalización |
| 💱 Convertidor | Conversión entre cualquier cripto y moneda fiat |
| 📉 Historial | Precios históricos con estadísticas del período |
| 🔥 Trending | Top 7 criptos más buscadas en 24h |
| 🔍 Buscador | Búsqueda por nombre o símbolo |
| 🏦 Exchanges | Top exchanges por volumen de trading |
| 🌍 Global | Resumen del mercado cripto mundial |

---

## 🏗 Arquitectura

```
crypto-api/
├── app/
│   ├── main.py                    # Entry point FastAPI
│   ├── api/
│   │   └── v1/
│   │       ├── router.py          # Router v1
│   │       └── endpoints/
│   │           └── crypto.py      # Todos los endpoints
│   ├── core/
│   │   └── config.py              # Configuración (Settings)
│   ├── models/
│   │   └── schemas.py             # Pydantic schemas
│   └── services/
│       └── coingecko.py           # Capa de integración CoinGecko
├── tests/
│   └── test_api.py                # Tests con pytest
├── requirements.txt
└── README.md
```

---

## 🔗 Endpoints

Base URL: `http://localhost:8000/api/v1`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del API y servicios externos |
| `GET` | `/markets` | Top criptos con datos de mercado completos |
| `GET` | `/coins/price` | Precio(s) de una o varias criptomonedas |
| `GET` | `/coins/{id}` | Detalle completo de una criptomoneda |
| `GET` | `/coins/{id}/history` | Historial de precios (N días) |
| `GET` | `/trending` | Top 7 criptos en tendencia (24h) |
| `GET` | `/convert` | Convertir entre cripto y fiat |
| `GET` | `/global` | Resumen global del mercado |
| `GET` | `/search` | Buscar criptomonedas por nombre/símbolo |
| `GET` | `/exchanges` | Top exchanges por volumen |

### Ejemplos de Requests

```bash
# Top 10 criptomonedas en USD
GET /api/v1/markets?currency=usd&per_page=10

# Precio de Bitcoin y Ethereum en USD y EUR
GET /api/v1/coins/price?ids=bitcoin,ethereum&currencies=usd,eur

# Convertir 2.5 BTC a USD
GET /api/v1/convert?from_coin=bitcoin&to_currency=usd&amount=2.5

# Historial de Ethereum últimos 30 días
GET /api/v1/coins/ethereum/history?days=30

# Buscar "solana"
GET /api/v1/search?q=solana
```

---

## 🚀 Instalación

### Requisitos
- Python 3.11+
- pip

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/crypto-api.git
cd crypto-api

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el servidor
uvicorn app.main:app --reload

# ✅ API disponible en: http://localhost:8000
# 📚 Docs interactivos: http://localhost:8000/docs
# 📖 ReDoc:             http://localhost:8000/redoc
```

---

## 📖 Uso

### Documentación interactiva (Swagger)

FastAPI genera automáticamente una interfaz **Swagger UI** disponible en `/docs`:

```
http://localhost:8000/docs
```

### Ejemplo de respuesta — `/api/v1/markets`

```json
{
  "success": true,
  "currency": "usd",
  "page": 1,
  "per_page": 5,
  "count": 5,
  "data": [
    {
      "id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "current_price": 95243.18,
      "market_cap": 1884000000000,
      "market_cap_rank": 1,
      "total_volume": 48200000000,
      "price_change_percentage_24h": 1.32,
      "price_change_percentage_7d_in_currency": 5.41,
      "ath": 108000.0,
      "ath_date": "2024-12-17T00:00:00.000Z"
    }
  ],
  "timestamp": "2025-04-18T00:00:00.000000"
}
```

### Ejemplo de respuesta — `/api/v1/convert`

```json
{
  "success": true,
  "data": {
    "from_coin": "bitcoin",
    "to_currency": "usd",
    "amount": 2.5,
    "rate": 95243.18,
    "result": 238107.95,
    "formatted": "2.5 BITCOIN = 238,107.950000 USD"
  },
  "timestamp": "2025-04-18T00:00:00.000000"
}
```

---

## 📸 Screenshots

### API corriendo localmente

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Swagger UI — Documentación interactiva (`/docs`)

> Accede a `http://localhost:8000/docs` después de iniciar el servidor.
> Verás todos los endpoints listados con descripción, parámetros y posibilidad de probarlos directamente.

```
💰 CryptoAPI
Version: 1.0.0

Endpoints disponibles:
  📁 Sistema
    GET /api/v1/health      — Estado del API
  📁 Mercados
    GET /api/v1/markets     — Top criptos con datos de mercado
    GET /api/v1/global      — Resumen global del mercado
  📁 Precios
    GET /api/v1/coins/price — Precio(s) simple(s)
  📁 Monedas
    GET /api/v1/coins/{id}  — Detalle de criptomoneda
  📁 Historial
    GET /api/v1/coins/{id}/history
  📁 Tendencias
    GET /api/v1/trending
  📁 Conversión
    GET /api/v1/convert
  📁 Búsqueda
    GET /api/v1/search
  📁 Exchanges
    GET /api/v1/exchanges
```

### Tests pasando ✅

```
$ pytest tests/ -v

============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.3.3
collected 9 items

tests/test_api.py::test_root                    PASSED  [ 11%]
tests/test_api.py::test_health                  PASSED  [ 22%]
tests/test_api.py::test_get_markets             PASSED  [ 33%]
tests/test_api.py::test_get_price               PASSED  [ 44%]
tests/test_api.py::test_get_trending            PASSED  [ 55%]
tests/test_api.py::test_convert                 PASSED  [ 66%]
tests/test_api.py::test_search                  PASSED  [ 77%]
tests/test_api.py::test_search_too_short        PASSED  [ 88%]
tests/test_api.py::test_convert_invalid_coin    PASSED  [100%]

======================== 9 passed in 1.63s =============================
```

---

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con reporte de cobertura
pytest tests/ -v --tb=short
```

Los tests incluyen:
- ✅ Endpoints básicos (root, health)
- ✅ Datos de mercado
- ✅ Precios simples
- ✅ Trending
- ✅ Conversión de monedas
- ✅ Búsqueda
- ✅ Validaciones (query muy corta, moneda inválida)

---

## 🛠 Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | 0.115 | Framework web principal |
| [Uvicorn](https://www.uvicorn.org) | 0.32 | Servidor ASGI |
| [Pydantic](https://docs.pydantic.dev) | 2.9 | Validación de datos y schemas |
| [httpx](https://www.python-httpx.org) | 0.27 | Cliente HTTP asíncrono |
| [pytest](https://pytest.org) | 8.3 | Framework de testing |
| [CoinGecko API](https://www.coingecko.com/api) | v3 | Fuente de datos (gratuita) |

---

## 📄 Licencia

MIT © 2025 — CryptoAPI Team
