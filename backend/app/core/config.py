from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Security QA MCP API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./security_qa.db"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
