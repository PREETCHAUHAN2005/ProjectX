from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Env-driven settings. Extra product APIs/auth are not source-confirmed."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    # IMPLEMENTATION: seed a readable post/comment/emotion scenario for local demos.
    # Default on in development so `uvicorn` is recordable without Redis/Telegram.
    demo_seed: bool = True
    demo_tick_seconds: float = 4.0

    redis_url: str = "redis://127.0.0.1:6379/0"
    mongodb_uri: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    telegram_session: str = ""

    x_ingestion_backend: str = "ntscraper"
    x_bearer_token: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
