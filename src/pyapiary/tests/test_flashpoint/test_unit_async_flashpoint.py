import pytest
import httpx
from unittest.mock import patch, AsyncMock
from pyapiary.api_connectors.flashpoint import AsyncFlashpointConnector


@pytest.mark.asyncio
async def test_async_init_with_api_key():
    connector = AsyncFlashpointConnector(api_key="test_token")
    assert connector.api_key == "test_token"
    assert connector.headers["Authorization"] == "Bearer test_token"


@patch.dict("os.environ", {"FLASHPOINT_API_KEY": "env_token"}, clear=True)
@pytest.mark.asyncio
async def test_async_init_with_env_key():
    connector = AsyncFlashpointConnector(load_env_vars=True)
    assert connector.api_key == "env_token"
    assert connector.headers["Authorization"] == "Bearer env_token"


@pytest.mark.asyncio
async def test_async_init_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="FLASHPOINT_API_KEY is required"):
            AsyncFlashpointConnector()


@patch("pyapiary.api_connectors.flashpoint.AsyncFlashpointConnector.post", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_search_fraud_checks(mock_post):
    import json

    request = httpx.Request("POST", "https://api.flashpoint.io/mock")
    payload = {"success": True, "data": []}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_post.return_value = mock_response

    connector = AsyncFlashpointConnector(api_key="mock_token")
    result = await connector.search_fraud_checks("stolen checks")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_post.assert_awaited_once_with(
        "/sources/v2/fraud/checks", json={"query": "stolen checks"}
    )


@patch("pyapiary.api_connectors.flashpoint.AsyncFlashpointConnector.post", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_search_fraud_checks_with_kwargs(mock_post):
    import json

    request = httpx.Request("POST", "https://api.flashpoint.io/mock")
    payload = {"success": True, "data": [{"id": "abc123"}]}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_post.return_value = mock_response

    connector = AsyncFlashpointConnector(api_key="mock_token")
    result = await connector.search_fraud_checks("routing number", size=10, from_=0)

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_post.assert_awaited_once_with(
        "/sources/v2/fraud/checks",
        json={"query": "routing number", "size": 10, "from_": 0},
    )


@patch("pyapiary.api_connectors.flashpoint.AsyncFlashpointConnector.post", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_search_fraud(mock_post):
    import json

    request = httpx.Request("POST", "https://api.flashpoint.io/mock")
    payload = {"success": True, "data": []}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_post.return_value = mock_response

    connector = AsyncFlashpointConnector(api_key="mock_token")
    result = await connector.search_fraud("credential stuffing")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_post.assert_awaited_once()