from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    awx_base_url: str
    awx_token: str
    llm_endpoint: str
    llm_model: str
    llm_api_key: str | None = None
    llm_provider: str = "default"
    jwt_secret: str
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    audit_log_dir: str = "/var/log/mcp"

settings = Settings()
