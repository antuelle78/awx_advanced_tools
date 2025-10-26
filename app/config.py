from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    awx_base_url: Optional[str] = None
    awx_token: Optional[str] = None
    awx_username: Optional[str] = None
    awx_password: Optional[str] = None
    llm_endpoint: Optional[str] = None
    llm_provider: str = "ollama"
    llm_model: str = "gpt-4o"
    llm_api_key: Optional[str] = None
    audit_log_dir: str = "/tmp/audit"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
