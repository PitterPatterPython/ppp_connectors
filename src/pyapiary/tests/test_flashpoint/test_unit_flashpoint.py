import httpx
import pytest
from unittest.mock import patch, MagicMock
from pyapiary.api_connectors.flashpoint import FlashpointConnector

def test_init_with_api_key():
    connector = FlashpointConnector(api_key="test_token")
    assert connector.api_key == "test_token"
    assert connector.headers["Authorization"] == "Bearer test_token"


@patch.dict("os.environ", {"FLASHPOINT_API_KEY": "env_token"}, clear=True)
def test_init_with_env_key():
    connector = FlashpointConnector(load_env_vars=True)
    assert connector.api_key == "env_token"
    assert connector.headers["Authorization"] == "Bearer env_token"


def test_init_missing_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="FLASHPOINT_API_KEY is required"):
            FlashpointConnector()


@patch("pyapiary.api_connectors.flashpoint.FlashpointConnector.post")
def test_search_fraud_checks(mock_post):
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

    connector = FlashpointConnector(api_key="mock_token")
    result = connector.search_fraud_checks("stolen checks")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_post.assert_called_once_with(
        "/sources/v2/fraud/checks", json={"query": "stolen checks"}
    )


@patch("pyapiary.api_connectors.flashpoint.FlashpointConnector.post")
def test_search_fraud_checks_with_kwargs(mock_post):
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

    connector = FlashpointConnector(api_key="mock_token")
    result = connector.search_fraud_checks("routing number", size=10, from_=0)

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_post.assert_called_once_with(
        "/sources/v2/fraud/checks",
        json={"query": "routing number", "size": 10, "from_": 0},
    )


@patch("pyapiary.api_connectors.flashpoint.FlashpointConnector.post")
def test_search_fraud(mock_post):
    import json

    # Use a real httpx.Response so our test matches the new return type
    request = httpx.Request("POST", "https://api.flashpoint.io/mock")
    payload = {"success": True, "data": []}
    mock_response = httpx.Response(
        200,
        request=request,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    mock_post.return_value = mock_response

    connector = FlashpointConnector(api_key="mock_token")
    result = connector.search_fraud("credential stuffing")

    assert isinstance(result, httpx.Response)
    assert result.json() == payload
    mock_post.assert_called_once()