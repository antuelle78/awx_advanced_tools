from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    awx_base_url: str = Field(..., env="AWX_BASE_URL")
    awx_token: str = Field(..., env="AWX_TOKEN")
    llm_endpoint: str = Field(..., env="LLM_ENDPOINT")
    llm_model: str = Field(..., env="LLM_MODEL")
    llm_api_key: str | None = Field(None, env="LLM_API_KEY")
    llm_provider: str = Field("default", env="LLM_PROVIDER")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
    audit_log_dir: str = Field("/var/log/mcp", env="AUDIT_LOG_DIR")

    class Config:
        env_file = ".env"

settings = Settings()
