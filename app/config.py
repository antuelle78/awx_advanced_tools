from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    awx_base_url: Optional[str] = "dummy"
    awx_token: Optional[str] = "your_awx_token"
    awx_username: Optional[str] = None
    awx_password: Optional[str] = None
    llm_endpoint: Optional[str] = None
    llm_provider: str = "ollama"
    llm_model: str = "dummy"
    llm_api_key: Optional[str] = None
    audit_log_dir: str = "/tmp/audit"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
