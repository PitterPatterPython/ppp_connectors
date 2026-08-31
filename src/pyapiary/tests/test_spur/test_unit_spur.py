import httpx
import pytest
from unittest.mock import patch
from pyapiary.api_connectors.spur import SpurConnector


def test_init_with_api_key():
    connector = SpurConnector(api_key="test_token")
    assert connector.api_key == "test_token"
    assert connector.headers["Token"] == "test_token"


@patch.dict("os.environ", {"SPUR_API_KEY": "env_token"}, clear=True)
def test_init_with_env_key():
    connector = SpurConnector(load_env_vars=True)
    assert connector.api_key == "env_token"
    assert connector.headers["Token"] == "env_token"


def test_init_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="SPUR_API_KEY is required"):
            SpurConnector()


@patch("pyapiary.api_connectors.spur.SpurConnector.get")
def test_context(mock_get):
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

    connector = SpurConnector(api_key="mock_token")
    result = connector.context("1.2.3.4")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_called_once_with("/v2/context/1.2.3.4", params={})


@patch("pyapiary.api_connectors.spur.SpurConnector.get")
def test_context_with_kwargs(mock_get):
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

    connector = SpurConnector(api_key="mock_token")
    result = connector.context("1.2.3.4", mmgeo=1)

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_called_once_with("/v2/context/1.2.3.4", params={"mmgeo": 1})


@patch("pyapiary.api_connectors.spur.SpurConnector.get")
def test_tag_metadata(mock_get):
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

    connector = SpurConnector(api_key="mock_token")
    result = connector.tag_metadata("VPN")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_called_once_with("/v2/metadata/tags/VPN", params={})


@patch("pyapiary.api_connectors.spur.SpurConnector.get")
def test_status(mock_get):
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

    connector = SpurConnector(api_key="mock_token")
    result = connector.status()

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_get.assert_called_once_with("/status", params={})
