import json
import httpx
import pytest
from unittest.mock import patch
from pyapiary.api_connectors.opencti import AsyncOpenCTIConnector
from pyapiary.api_connectors import opencti_queries as q


def _resp(payload=None):
    req = httpx.Request("POST", "https://octi.test/graphql")
    return httpx.Response(
        200,
        request=req,
        content=json.dumps(payload or {"data": {}}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


@pytest.mark.asyncio
@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
async def test_async_init_explicit(_env):
    c = AsyncOpenCTIConnector(url="https://octi.test", token="tok")
    assert c.base_url == "https://octi.test"
    assert c.headers["Authorization"] == "Bearer tok"


@pytest.mark.asyncio
@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
async def test_async_init_missing_token_raises(_env):
    with pytest.raises(ValueError, match="token"):
        AsyncOpenCTIConnector(url="https://octi.test")


@pytest.mark.asyncio
@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
async def test_async_search_entities(_env):
    c = AsyncOpenCTIConnector(url="https://octi.test", token="tok")
    captured = {}

    async def fake_execute(query, variables=None, raise_on_errors=True):
        captured["query"] = query
        captured["vars"] = variables
        return _resp()

    c.execute = fake_execute
    result = await c.search_entities(types=["Malware"], first=3)
    assert isinstance(result, httpx.Response)
    assert captured["query"] == q.SEARCH_ENTITIES_QUERY
    assert captured["vars"]["types"] == ["Malware"]
    assert captured["vars"]["first"] == 3


@pytest.mark.asyncio
@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
async def test_async_get_relationships_normalizes(_env):
    c = AsyncOpenCTIConnector(url="https://octi.test", token="tok")
    captured = {}

    async def fake_execute(query, variables=None, raise_on_errors=True):
        captured["vars"] = variables
        return _resp()

    c.execute = fake_execute
    await c.get_relationships(from_id="abc", relationship_type="uses")
    assert captured["vars"]["fromId"] == ["abc"]
    assert captured["vars"]["relationship_type"] == ["uses"]
