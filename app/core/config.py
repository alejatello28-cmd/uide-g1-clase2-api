from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CryptoAPI"
    VERSION: str = "1.0.0"

    # CoinGecko (free tier - no key needed)
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"

    # Cache TTL in seconds
    CACHE_TTL: int = 60

    class Config:
        case_sensitive = True


settings = Settings()
