from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "API Monitor"
    environment: str = "development"
    database_url: str = "sqlite:///./api_monitor.db"
    check_timeout_seconds: float = 8.0
    max_response_bytes: int = 1_048_576
    scheduler_enabled: bool = False
    scheduler_max_concurrent_checks: int = 5
    api_key: str = ""


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
