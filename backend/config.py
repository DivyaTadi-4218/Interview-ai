"""
Central configuration, loaded from environment variables / .env.
Never hardcode API keys — everything sensitive comes from here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    database_url: str = "sqlite:///./interview.db"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
