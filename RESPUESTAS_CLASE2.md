# Trabajo Final — Módulo de Tratamiento de Datos
## Repositorio: uide-g1-clase2-api (CryptoAPI)

---

## Pregunta 1: Explotación del endpoint `/coins/price` y sus consecuencias

### Contexto del endpoint

El endpoint `GET /api/v1/coins/price` permite consultar el precio de **una o varias criptomonedas** sin ningún tipo de autenticación. Internamente, el servicio `services/coingecko.py` reenvía esa solicitud directamente a la API pública de CoinGecko. Esto convierte al sistema en un **proxy abierto y sin restricciones**.

Ejemplo de uso legítimo:
```
GET /api/v1/coins/price?ids=bitcoin,ethereum&currencies=usd,eur
```
---
INTEGRANTE: Alejandra Tello
### 1. El endpoint /coins/price permite consultar múltiples criptomonedas sin autenticación, actuando en la práctica como un proxy hacia CoinGecko.
### Cómo podría un atacante explotar este endpoint para realizar un abuso masivo, y cuáles serían las consecuencias específicas para su sistema y para el servicio externo?

Un atacante puede abusar de este endpoint de varias formas concretas:
#### 1. Ataque de fuerza bruta por volumen (Scraping masivo)
El atacante lanza miles de peticiones automatizadas en poco tiempo, consultando la mayor cantidad posible de criptomonedas y monedas fiat simultáneamente:
```bash
# Script de ataque simple con curl en bucle
while true; do
  curl "http://tu-api.com/api/v1/coins/price?ids=bitcoin,ethereum,solana,cardano,polkadot&currencies=usd,eur,gbp,jpy"
done

# O con una herramienta como ab (Apache Benchmark)
ab -n 10000 -c 100 "http://tu-api.com/api/v1/coins/price?ids=bitcoin,ethereum"
```

**Lo que el atacante logra:** extraer datos financieros en tiempo real de forma gratuita e ilimitada, usando los recursos y el límite de API de CoinGecko que le corresponden al sistema.
---

#### 2. Amplificación de solicitudes (Multiplexing attack)

El endpoint acepta múltiples `ids` y `currencies` en una sola petición. Esto significa que **una sola solicitud al sistema puede generar una solicitud mucho más costosa hacia CoinGecko**:

```
# 1 petición al sistema → 1 petición a CoinGecko con mucha carga
GET /api/v1/coins/price?ids=bitcoin,ethereum,solana,cardano,polkadot,
    chainlink,avalanche,polygon,cosmos,algorand&currencies=usd,eur,
    gbp,jpy,aud,cad,chf,cny,hkd,nok
```

El atacante envía peticiones simples pero con parámetros maximizados, amplificando el consumo del rate limit de CoinGecko con mínimo esfuerzo propio.

---

#### 3. Uso del sistema como infraestructura gratuita

Sin autenticación, cualquier persona o empresa puede usar la API como si fuera propia para alimentar sus propias aplicaciones o dashboards comerciales, sin pagar ni registrarse en CoinGecko directamente.

---

### Consecuencias específicas para el sistema

| Consecuencia | Descripción |
|---|---|
| **Agotamiento de recursos del servidor** | El servidor FastAPI/Uvicorn procesa miles de peticiones concurrentes, agotando CPU, memoria y conexiones disponibles |
| **Degradación del servicio** | Los usuarios legítimos experimentan timeouts y respuestas lentas porque el servidor está saturado |
| **Costos de infraestructura disparados** | Si el sistema corre en un servicio cloud (AWS, GCP, etc.), el tráfico excesivo genera cargos económicos inesperados |
| **Sin trazabilidad del atacante** | Al no haber autenticación, es imposible identificar quién está abusando del sistema o bloquear a un usuario específico |
| **Sin capacidad de respuesta** | Sin rate limiting implementado, el sistema no puede distinguir entre un usuario legítimo y un atacante automatizado |

---

### Consecuencias específicas para CoinGecko (servicio externo)

Esta es la consecuencia más crítica. La API pública gratuita de CoinGecko tiene **límites estrictos de uso**:

| Plan CoinGecko | Límite de solicitudes |
|---|---|
| Demo (gratuito) | ~30 solicitudes/minuto |
| Analyst | 500 solicitudes/minuto |
| Lite | 500 solicitudes/minuto |

Cuando el atacante satura el sistema con peticiones masivas, **todas esas peticiones se reenvían a CoinGecko usando las credenciales o IP del sistema**. Esto produce:

1. **Bloqueo de la API Key o IP**: CoinGecko detecta el uso abusivo y bloquea el acceso, dejando **toda la API inutilizable** para todos los usuarios legítimos.

2. **Error 429 (Too Many Requests)**: El sistema comienza a devolver errores a todos sus usuarios porque CoinGecko rechaza las peticiones que superan el límite.

3. **Suspensión de cuenta**: Si el sistema usa un plan de pago, CoinGecko puede suspender la cuenta por violación de términos de servicio.

4. **El atacante no sufre consecuencias**: El rate limit se consume en la cuenta del sistema, no en la del atacante.

**Flujo del ataque:**
```
Atacante (10,000 req/min)
        ↓
[Sistema CryptoAPI — sin rate limiting]
        ↓  (reenvía todo a CoinGecko)
[CoinGecko — límite: 30 req/min]
        ↓
❌ Error 429 — IP/API Key bloqueada
        ↓
Todos los usuarios legítimos reciben error
```

---

### ¿Cómo mitigar estos riesgos?

Para resolver los problemas identificados, se recomienda implementar las siguientes medidas en el proyecto:

#### 1. Rate Limiting por IP (solución inmediata)

```python
# Instalar: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/coins/price")
@limiter.limit("10/minute")  # Máximo 10 peticiones por minuto por IP
async def get_price(request: Request, ids: str, currencies: str = "usd"):
    return await coingecko_service.get_price(ids, currencies)
```

#### 2. Autenticación con API Key

```python
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@router.get("/coins/price")
async def get_price(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="API Key inválida")
    ...
```

#### 3. Caché de respuestas

Dado que los precios no cambian cada segundo, se puede cachear la respuesta de CoinGecko por 60 segundos, reduciendo drásticamente las solicitudes al servicio externo:

```python
# Instalar: pip install cachetools
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=60)  # Caché de 60 segundos

async def get_price(ids: str, currencies: str):
    cache_key = f"{ids}_{currencies}"
    if cache_key in cache:
        return cache[cache_key]  # Respuesta desde caché
    
    result = await coingecko_client.get_price(ids, currencies)
    cache[cache_key] = result
    return result
```

#### 4. Limitar los parámetros de entrada

```python
@router.get("/coins/price")
async def get_price(ids: str, currencies: str = "usd"):
    # Limitar cantidad de ids por petición
    ids_list = ids.split(",")
    if len(ids_list) > 5:
        raise HTTPException(
            status_code=400,
            detail="Máximo 5 criptomonedas por consulta"
        )
    ...
```

### Resumen

| Vector de ataque | Consecuencia en el sistema | Consecuencia en CoinGecko |
|---|---|---|
| Peticiones masivas automatizadas | Saturación del servidor, caída del servicio | Rate limit agotado, IP bloqueada |
| Amplificación con múltiples `ids` | Alto consumo de recursos por petición | Solicitudes costosas reenvíadas |
| Uso como proxy gratuito | Costos de infraestructura, sin control de usuarios | Violación de términos de servicio |

**La ausencia de autenticación, rate limiting y caché convierte al endpoint `/coins/price` en el vector de ataque más crítico del sistema**, ya que un atacante puede dejar inoperativa la API completa simplemente enviando peticiones en bucle, sin necesidad de conocimientos avanzados.

---
INTEGRANTE: Luis Alexander Soto Segovia

## 1) Riesgos de Abuso del Endpoint

### ¿Cómo podría explotarse?
Un atacante podría automatizar múltiples solicitudes (scripts o bots) enviando peticiones masivas al endpoint, utilizando listas extensas de criptomonedas y monedas, sin ningún tipo de restricción.

### Consecuencias para el sistema:
- Alto consumo de CPU, memoria y ancho de banda.
- Saturación del backend.
- Aumento de latencia para usuarios legítimos.
- Posible caída del servicio.
- Bloqueo de la IP del servidor por parte de CoinGecko.
- Incremento de costos en infraestructura (cloud).

### Consecuencias para CoinGecko:
- Tráfico abusivo proveniente de su sistema.
- Consumo indebido de su API pública.
- Violación de límites o términos de uso.
- Bloqueo del acceso desde su IP.

### Recomendaciones:
- Implementar autenticación (API Key, JWT).
- Aplicar **rate limiting** por IP o usuario.
- Limitar la cantidad de `ids` y `currencies` por solicitud.
- Implementar caché para respuestas frecuentes.
- Monitorear logs y detectar patrones anómalos.

---

## 2) Desventajas del Scraper (Tipo de Información)

- **Información incompleta:** no todas las criptomonedas tienen datos completos.
- **Datos desactualizados:** los precios pueden cambiar rápidamente.
- **Dependencia de terceros:** cambios en CoinGecko afectan directamente al sistema.
- **Datos no verificados:** la calidad depende de la fuente externa.
- **Limitaciones de uso:** posibles bloqueos por exceso de consultas.
- **Cambios en el formato:** si la API cambia, el scraper puede fallar.
- **Cobertura limitada:** no todos los mercados o exchanges están incluidos.

---

## Conclusión
El endpoint, en su estado actual, representa un riesgo significativo al actuar como proxy abierto. Es fundamental implementar controles de seguridad y optimización para evitar abusos y garantizar la disponibilidad del servicio.
