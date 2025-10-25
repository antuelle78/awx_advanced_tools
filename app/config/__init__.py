from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    awx_base_url: str = "dummy"
    awx_token: str = "dummy"
    llm_endpoint: str = "dummy"
    llm_model: str = "dummy"
    llm_api_key: str | None = None
    llm_provider: str = "default"
    jwt_secret: str = "dummy"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    audit_log_dir: str = "/var/log/mcp"

settings = Settings()
