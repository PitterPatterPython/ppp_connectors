import json
import httpx
import pytest
from pyapiary.api_connectors.graphql import AsyncGraphQLConnector, GraphQLError


def _resp(payload, status=200):
    req = httpx.Request("POST", "https://example.test/graphql")
    return httpx.Response(
        status,
        request=req,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


@pytest.mark.asyncio
async def test_async_execute_returns_httpx_response():
    c = AsyncGraphQLConnector(base_url="https://example.test")

    async def fake_post(endpoint, json=None):
        return _resp({"data": {"ok": 1}})

    c.post = fake_post
    result = await c.execute("query { ok }")
    assert isinstance(result, httpx.Response)
    assert result.json()["data"]["ok"] == 1


@pytest.mark.asyncio
async def test_async_execute_sends_query_and_variables():
    c = AsyncGraphQLConnector(base_url="https://example.test", endpoint="/graphql")
    captured = {}

    async def fake_post(endpoint, json=None):
        captured["endpoint"] = endpoint
        captured["json"] = json
        return _resp({"data": {}})

    c.post = fake_post
    await c.execute("query Q { a }", {"x": 1})
    assert captured["endpoint"] == "/graphql"
    assert captured["json"] == {"query": "query Q { a }", "variables": {"x": 1}}


@pytest.mark.asyncio
async def test_async_execute_raises_graphql_error():
    c = AsyncGraphQLConnector(base_url="https://example.test")

    async def fake_post(endpoint, json=None):
        return _resp({"errors": [{"message": "boom"}]})

    c.post = fake_post
    with pytest.raises(GraphQLError, match="boom"):
        await c.execute("query { bad }")


@pytest.mark.asyncio
async def test_async_execute_no_raise_when_disabled():
    c = AsyncGraphQLConnector(base_url="https://example.test")

    async def fake_post(endpoint, json=None):
        return _resp({"errors": [{"message": "boom"}]})

    c.post = fake_post
    result = await c.execute("query { bad }", raise_on_errors=False)
    assert isinstance(result, httpx.Response)
    assert result.json()["errors"][0]["message"] == "boom"
