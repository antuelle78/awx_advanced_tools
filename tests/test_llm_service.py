import os
import pytest
from unittest.mock import patch, AsyncMock
from app.llm.service import PromptService

# Set default provider to ollama to avoid import errors
os.environ["LLM_PROVIDER"] = "ollama"


class TestPromptService:
    @patch("app.llm.service.get_llm_client")
    @patch("app.llm.service.TEMPLATES")
    @patch("app.llm.service.get_schema")
    async def test_generate_payload_success(self, mock_get_schema, mock_templates, mock_get_client):
        # Mock LLM client
        mock_client = AsyncMock()
        mock_client.get_payload = AsyncMock(return_value={"name": "test"})
        mock_get_client.return_value = mock_client

        # Mock templates
        mock_templates.__contains__ = lambda self, key: key == "test_action"
        mock_templates.__getitem__ = lambda self, key: "Prompt for {name}"

        # Mock schema
        mock_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        mock_get_schema.return_value = mock_schema

        service = PromptService()
        result = await service.generate_payload("test_action", {"name": "test"})

        assert result == {"name": "test"}
        mock_client.get_payload.assert_called_once()

    @patch("app.llm.service.get_llm_client")
    @patch("app.llm.service.TEMPLATES")
    async def test_generate_payload_unknown_action(self, mock_templates, mock_get_client):
        mock_templates.__contains__ = lambda self, key: False
        service = PromptService()
        with pytest.raises(ValueError, match="Unknown action"):
            await service.generate_payload("unknown", {})

    @patch("app.llm.service.get_llm_client")
    @patch("app.llm.service.TEMPLATES")
    @patch("app.llm.service.get_schema")
    async def test_generate_payload_cache_hit(self, mock_get_schema, mock_templates, mock_get_client):
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        mock_templates.__contains__ = lambda self, key: True
        mock_templates.__getitem__ = lambda self, key: "Prompt for {name}"
        mock_get_schema.return_value = {"type": "object"}

        service = PromptService()
        # First call
        await service.generate_payload("test_action", {"name": "test"})
        # Second call should use cache
        await service.generate_payload("test_action", {"name": "test"})
        # LLM should only be called once
        mock_client.get_payload.assert_called_once()

    @patch("app.llm.service.get_llm_client")
    @patch("app.llm.service.TEMPLATES")
    @patch("app.llm.service.get_schema")
    async def test_generate_payload_validation_error(self, mock_get_schema, mock_templates, mock_get_client):
        mock_client = AsyncMock()
        mock_client.get_payload = AsyncMock(return_value={"invalid": "data"})
        mock_get_client.return_value = mock_client
        mock_templates.__contains__ = lambda self, key: True
        mock_templates.__getitem__ = lambda self, key: "Prompt"
        mock_get_schema.return_value = {"type": "object", "required": ["name"]}

        service = PromptService()
        with pytest.raises(ValueError, match="LLM payload does not match schema"):
            await service.generate_payload("test_action", {})