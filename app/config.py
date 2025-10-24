from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    awx_base_url: str
    awx_token: str
    llm_endpoint: str
    jwt_secret: str
    audit_log_dir: str = "/var/log/audit"

    class Config:
        env_prefix = ""

settings = Settings()