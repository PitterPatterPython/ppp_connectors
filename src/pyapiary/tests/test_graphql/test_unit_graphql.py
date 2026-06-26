import json
import httpx
import pytest
from pyapiary.api_connectors.graphql import GraphQLConnector, GraphQLError


def _resp(payload, status=200):
    req = httpx.Request("POST", "https://example.test/graphql")
    return httpx.Response(
        status,
        request=req,
        content=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


def test_init_sets_endpoint():
    c = GraphQLConnector(base_url="https://example.test")
    assert c.base_url == "https://example.test"
    assert c.endpoint == "/graphql"
    c2 = GraphQLConnector(base_url="https://example.test", endpoint="/api/graphql")
    assert c2.endpoint == "/api/graphql"


def test_execute_returns_httpx_response():
    c = GraphQLConnector(base_url="https://example.test")
    c.post = lambda endpoint, json=None: _resp({"data": {"ok": 1}})
    result = c.execute("query { ok }")
    assert isinstance(result, httpx.Response)
    assert result.json()["data"]["ok"] == 1


def test_execute_sends_query_and_variables_to_endpoint():
    c = GraphQLConnector(base_url="https://example.test", endpoint="/graphql")
    captured = {}

    def fake_post(endpoint, json=None):
        captured["endpoint"] = endpoint
        captured["json"] = json
        return _resp({"data": {}})

    c.post = fake_post
    c.execute("query Q { a }", {"x": 1})
    assert captured["endpoint"] == "/graphql"
    assert captured["json"] == {"query": "query Q { a }", "variables": {"x": 1}}


def test_execute_defaults_variables_to_empty_dict():
    c = GraphQLConnector(base_url="https://example.test")
    captured = {}

    def fake_post(endpoint, json=None):
        captured["json"] = json
        return _resp({"data": {}})

    c.post = fake_post
    c.execute("query { a }")
    assert captured["json"]["variables"] == {}


def test_execute_raises_graphql_error_on_200_errors():
    c = GraphQLConnector(base_url="https://example.test")
    c.post = lambda endpoint, json=None: _resp({"errors": [{"message": "boom"}]})
    with pytest.raises(GraphQLError, match="boom"):
        c.execute("query { bad }")


def test_execute_no_raise_when_disabled():
    c = GraphQLConnector(base_url="https://example.test")
    c.post = lambda endpoint, json=None: _resp({"errors": [{"message": "boom"}]})
    result = c.execute("query { bad }", raise_on_errors=False)
    assert isinstance(result, httpx.Response)
    assert result.json()["errors"][0]["message"] == "boom"


def test_graphql_error_carries_errors_and_message():
    err = GraphQLError([{"message": "a"}, {"message": "b"}])
    assert err.errors[0]["message"] == "a"
    assert str(err) == "a; b"
