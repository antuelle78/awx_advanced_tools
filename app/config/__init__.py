from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    awx_base_url: str | None = None
    awx_token: str | None = None
    awx_username: str | None = None
    awx_password: str | None = None
    llm_endpoint: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None
    llm_provider: str = "default"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    audit_log_dir: str = "/var/log/mcp"
    jwt_secret: str | None = None


settings = Settings()
