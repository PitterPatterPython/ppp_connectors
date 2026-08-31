import httpx
import pytest
from unittest.mock import patch, AsyncMock
from pyapiary.api_connectors.spur import AsyncSpurConnector


@pytest.mark.asyncio
async def test_async_init_with_api_key():
    connector = AsyncSpurConnector(api_key="test_token")
    assert connector.api_key == "test_token"
    assert connector.headers["Token"] == "test_token"


@patch.dict("os.environ", {"SPUR_API_KEY": "env_token"}, clear=True)
@pytest.mark.asyncio
async def test_async_init_with_env_key():
    connector = AsyncSpurConnector(load_env_vars=True)
    assert connector.api_key == "env_token"
    assert connector.headers["Token"] == "env_token"


@pytest.mark.asyncio
async def test_async_init_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="SPUR_API_KEY is required"):
            AsyncSpurConnector()


@patch("pyapiary.api_connectors.spur.AsyncSpurConnector.get", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_context(mock_get):
    import json

    request = httpx.Request("GET", "https://api.spur.us/mock")
    payload = {"as": {"number": 12345}, "ip": "1.2.3.4"}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_get.return_value = mock_response

    connector = AsyncSpurConnector(api_key="mock_token")
    result = await connector.context("1.2.3.4")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_awaited_once_with("/v2/context/1.2.3.4", params={})


@patch("pyapiary.api_connectors.spur.AsyncSpurConnector.get", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_context_with_kwargs(mock_get):
    import json

    request = httpx.Request("GET", "https://api.spur.us/mock")
    payload = {"as": {"number": 12345}, "ip": "1.2.3.4"}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_get.return_value = mock_response

    connector = AsyncSpurConnector(api_key="mock_token")
    result = await connector.context("1.2.3.4", mmgeo=1)

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_awaited_once_with("/v2/context/1.2.3.4", params={"mmgeo": 1})


@patch("pyapiary.api_connectors.spur.AsyncSpurConnector.get", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_tag_metadata(mock_get):
    import json

    request = httpx.Request("GET", "https://api.spur.us/mock")
    payload = {"tag": "VPN", "description": "Virtual Private Network"}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_get.return_value = mock_response

    connector = AsyncSpurConnector(api_key="mock_token")
    result = await connector.tag_metadata("VPN")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_awaited_once_with("/v2/metadata/tags/VPN", params={})


@patch("pyapiary.api_connectors.spur.AsyncSpurConnector.get", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_async_status(mock_get):
    import json

    request = httpx.Request("GET", "https://api.spur.us/mock")
    payload = {"active": True, "queriesRemaining": 1000, "tier": "enterprise"}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_get.return_value = mock_response

    connector = AsyncSpurConnector(api_key="mock_token")
    result = await connector.status()

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_awaited_once_with("/status", params={})
