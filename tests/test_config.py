from app.config import Settings


def test_settings_default_values(monkeypatch):
    monkeypatch.delenv("AWX_BASE_URL", raising=False)
    monkeypatch.delenv("AWX_TOKEN", raising=False)
    monkeypatch.delenv("AWX_USERNAME", raising=False)
    monkeypatch.delenv("AWX_PASSWORD", raising=False)
    monkeypatch.delenv("LLM_ENDPOINT", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    settings = Settings()
    assert settings.llm_provider == "ollama"
    assert settings.llm_model == "gpt-4o"
    assert settings.audit_log_dir == "/tmp/audit"
    assert settings.awx_base_url is None
    assert settings.awx_token is None


def test_settings_loading(monkeypatch):
    monkeypatch.setenv("AWX_BASE_URL", "http://awx.example.com")
    monkeypatch.setenv("AWX_TOKEN", "awx_token_123")
    monkeypatch.setenv("LLM_ENDPOINT", "http://llm.example.com")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "llama2")
    settings = Settings()
    assert settings.awx_base_url == "http://awx.example.com"
    assert settings.awx_token == "awx_token_123"
    assert settings.llm_endpoint == "http://llm.example.com"
    assert settings.llm_provider == "ollama"
    assert settings.llm_model == "llama2"


def test_settings_optional_fields(monkeypatch):
    monkeypatch.setenv("AWX_USERNAME", "admin")
    monkeypatch.setenv("AWX_PASSWORD", "pass")
    monkeypatch.setenv("LLM_API_KEY", "key123")
    settings = Settings()
    assert settings.awx_username == "admin"
    assert settings.awx_password == "pass"
    assert settings.llm_api_key == "key123"


def test_settings_env_file_fallback(monkeypatch):
    # Simulate .env file by setting env vars
    monkeypatch.setenv("AWX_BASE_URL", "from_env")
    settings = Settings()
    assert settings.awx_base_url == "from_env"
