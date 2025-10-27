import httpx
import pytest
from unittest.mock import AsyncMock, patch
from app.adapters.awx_service import awx_client, AWXClient


# Dummy response helper
class DummyResponse:
    def __init__(self, json_data: dict, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("Error", request=None, response=self)


async def dummy_post(url, json=None, headers=None):
    return DummyResponse({"url": url, "json": json, "headers": headers})


async def dummy_get(url, params=None, headers=None):
    return DummyResponse({"url": url, "params": params, "headers": headers})


async def dummy_patch(url, json=None, headers=None):
    return DummyResponse(
        {"method": "PATCH", "url": url, "json": json, "headers": headers}
    )


async def dummy_delete(url, headers=None):
    return DummyResponse({"method": "DELETE", "url": url, "headers": headers})


@pytest.fixture
def mock_httpx():
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None

        async def dummy_request(method, url, json=None, params=None, headers=None):
            return DummyResponse(
                {
                    "method": method,
                    "url": url,
                    "json": json,
                    "params": params,
                    "headers": headers,
                }
            )

        mock_instance.request = AsyncMock(side_effect=dummy_request)
        yield MockClient


@pytest.mark.asyncio
async def test_launch_job_template(mock_httpx):
    result = await awx_client.launch_job_template(10, {"var": "value"})
    assert result["url"].endswith("/job_templates/10/launch/")


@pytest.mark.asyncio
async def test_create_inventory(mock_httpx):
    result = await awx_client.create_inventory("test_inv", {"var": "val"})
    assert result["json"]["name"] == "test_inv"


@pytest.mark.asyncio
async def test_list_templates(mock_httpx):
    result = await awx_client.list_templates()
    assert result["url"].endswith("/job_templates/")

@pytest.mark.asyncio
async def test_create_job_template(mock_httpx):
    result = await awx_client.create_job_template("Test Job Template", 1, 1, "playbook.yml")
    assert result["json"]["name"] == "Test Job Template"

@pytest.mark.asyncio
async def test_create_host(mock_httpx):
    result = await awx_client.create_host({"name": "Test Host", "inventory": 1})
    assert result["json"]["name"] == "Test Host"

@pytest.mark.asyncio
async def test_validate_host_valid():
    client = AWXClient()
    assert client.validate_host({"name": "Test", "inventory": 1})

@pytest.mark.asyncio
async def test_validate_host_invalid():
    client = AWXClient()
    assert not client.validate_host({"name": "Test"})


# Delete user tests
@pytest.mark.asyncio
async def test_delete_user_success_with_json_response(mock_httpx):
    """Test successful user deletion with JSON response."""
    result = await awx_client.delete_user(123)
    assert result["method"] == "DELETE"
    assert "users/123/" in result["url"]


@pytest.mark.asyncio
async def test_delete_user_success_empty_response(mock_httpx):
    """Test successful user deletion with empty response (204 No Content)."""
    # Create a response that raises ValueError on json() call (simulating empty body)
    class EmptyResponse:
        def json(self):
            raise ValueError("No JSON content")

        def raise_for_status(self):
            pass  # No error for successful deletion

    # Mock the request to return empty response
    async def dummy_delete_request(method, url, json=None, params=None, headers=None):
        if method == "DELETE":
            return EmptyResponse()
        return DummyResponse({
            "method": method, "url": url, "json": json, "params": params, "headers": headers
        })

    mock_httpx.return_value.__aenter__.return_value.request = AsyncMock(side_effect=dummy_delete_request)

    result = await awx_client.delete_user(123)
    assert result == {"status": "deleted", "id": 123}


@pytest.mark.asyncio
async def test_delete_user_invalid_user_id():
    """Test delete_user with invalid user_id."""
    client = AWXClient()

    # Test negative user_id
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await client.delete_user(-1)

    # Test zero user_id
    with pytest.raises(ValueError, match="user_id must be a positive integer"):
        await client.delete_user(0)


@pytest.mark.asyncio
async def test_delete_user_http_error(mock_httpx):
    """Test delete_user with HTTP error responses."""
    async def dummy_error_request(method, url, json=None, params=None, headers=None):
        if method == "DELETE":
            return DummyResponse({"detail": "Not found"}, 404)
        return DummyResponse({
            "method": method, "url": url, "json": json, "params": params, "headers": headers
        })

    mock_httpx.return_value.__aenter__.return_value.request = AsyncMock(side_effect=dummy_error_request)

    # Test that HTTP errors are propagated
    with pytest.raises(httpx.HTTPStatusError):
        await awx_client.delete_user(999)
