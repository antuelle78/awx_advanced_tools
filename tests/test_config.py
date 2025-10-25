from app.config import Settings

# Test Settings loading from environment variables


def test_settings_loading(monkeypatch):
    # set env vars
    monkeypatch.setenv("AWX_BASE_URL", "http://awx.example.com")
    monkeypatch.setenv("AWX_TOKEN", "awx_token_123")
    monkeypatch.setenv("LLM_ENDPOINT", "http://llm.example.com")
    settings = Settings()
    assert settings.awx_base_url == "http://awx.example.com"
    assert settings.awx_token == "awx_token_123"
    assert settings.llm_endpoint == "http://llm.example.com"
