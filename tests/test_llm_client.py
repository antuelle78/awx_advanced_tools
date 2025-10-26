import os
import pytest
from unittest.mock import patch, AsyncMock
from app.llm.client import get_llm_client, OpenAIClient, OllamaClient
import app.llm.client as client_module

# Set default provider to ollama to avoid import errors
os.environ["LLM_PROVIDER"] = "ollama"


class TestGetLLMClient:
    @patch("app.llm.client.settings")
    def test_get_llm_client_ollama(self, mock_settings):
        mock_settings.llm_provider = "ollama"
        mock_settings.llm_endpoint = "http://localhost:11434"
        client = get_llm_client()
        assert isinstance(client, OllamaClient)

    @patch("app.llm.client.settings")
    @patch("importlib.util.find_spec")
    def test_get_llm_client_openai_available(self, mock_find_spec, mock_settings):
        mock_settings.llm_provider = "default"
        mock_find_spec.return_value = True  # OpenAI available
        client = get_llm_client()
        assert isinstance(client, OpenAIClient)

    @patch("app.llm.client.settings")
    @patch("importlib.util.find_spec")
    def test_get_llm_client_openai_unavailable_fallback_ollama(
        self, mock_find_spec, mock_settings
    ):
        mock_settings.llm_provider = "ollama"
        mock_settings.llm_endpoint = "http://localhost:11434"
        mock_find_spec.return_value = None  # OpenAI not available
        client = get_llm_client()
        assert isinstance(client, OllamaClient)

    @patch("app.llm.client.settings")
    @patch("importlib.util.find_spec")
    def test_get_llm_client_openai_unavailable_error(
        self, mock_find_spec, mock_settings
    ):
        mock_settings.llm_provider = "default"
        mock_find_spec.return_value = None  # OpenAI not available
        with pytest.raises(RuntimeError, match="OpenAI SDK not installed"):
            get_llm_client()


class TestOpenAIClient:
    @patch("app.llm.client.settings")
    @patch("app.llm.client.openai")
    def test_openai_client_init(self, mock_openai, mock_settings):
        if not hasattr(client_module, 'openai'):
            pytest.skip("openai not available")
        mock_settings.llm_endpoint = "http://example.com/v1/"
        mock_settings.llm_model = "gpt-3.5"
        mock_settings.llm_api_key = "test_key"
        client = OpenAIClient()
        assert client.api_key == "test_key"
        assert client.model == "gpt-3.5"

    @pytest.mark.asyncio
    @patch("app.llm.client.settings")
    @patch("app.llm.client.openai")
    async def test_openai_client_get_payload(self, mock_openai, mock_settings):
        if not hasattr(client_module, 'openai'):
            pytest.skip("openai not available")
        mock_settings.llm_model = "gpt-3.5"
        mock_settings.llm_api_key = "test_key"
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = '{"test": "data"}'
        mock_openai.ChatCompletion.acreate = AsyncMock(return_value=mock_response)
        client = OpenAIClient()
        result = await client.get_payload("test prompt")
        assert result == {"test": "data"}


class TestOllamaClient:
    @patch("app.llm.client.settings")
    @patch("app.llm.client.ollama")
    def test_ollama_client_init(self, mock_ollama, mock_settings):
        if not hasattr(client_module, 'ollama'):
            pytest.skip("ollama not available")
        mock_settings.llm_endpoint = "http://example.com"
        mock_settings.llm_model = "llama2"
        mock_ollama.AsyncClient.return_value = AsyncMock()
        client = OllamaClient()
        assert client.model == "llama2"

    @pytest.mark.asyncio
    @patch("app.llm.client.settings")
    @patch("app.llm.client.ollama")
    async def test_ollama_client_get_payload(self, mock_ollama, mock_settings):
        if not hasattr(client_module, 'ollama'):
            pytest.skip("ollama not available")
        mock_settings.llm_model = "llama2"
        mock_settings.llm_endpoint = "http://example.com"
        mock_client = AsyncMock()
        mock_response = {"response": '{"test": "data"}'}
        mock_client.generate = AsyncMock(return_value=mock_response)
        mock_ollama.AsyncClient.return_value = mock_client
        client = OllamaClient()
        result = await client.get_payload("test prompt")
        assert result == {"test": "data"}
