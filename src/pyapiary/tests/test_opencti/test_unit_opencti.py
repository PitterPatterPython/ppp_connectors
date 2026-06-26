import json
import httpx
import pytest
from unittest.mock import patch
from pyapiary.api_connectors.opencti import OpenCTIConnector
from pyapiary.api_connectors import opencti_queries as q


def _resp(payload=None):
    req = httpx.Request("POST", "https://octi.test/graphql")
    return httpx.Response(
        200,
        request=req,
        content=json.dumps(payload or {"data": {}}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_init_explicit_args(_env):
    c = OpenCTIConnector(url="https://octi.test", token="tok")
    assert c.base_url == "https://octi.test"
    assert c.token == "tok"
    assert c.headers["Authorization"] == "Bearer tok"
    assert c.headers["Content-Type"] == "application/json"
    assert c.endpoint == "/graphql"


@patch(
    "pyapiary.api_connectors.opencti.combine_env_configs",
    return_value={"OPENCTI_URL": "https://env.test", "OPENCTI_TOKEN": "envtok"},
)
def test_init_from_env(_env):
    c = OpenCTIConnector()
    assert c.base_url == "https://env.test"
    assert c.token == "envtok"
    assert c.headers["Authorization"] == "Bearer envtok"


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_init_missing_url_raises(_env):
    with pytest.raises(ValueError, match="url"):
        OpenCTIConnector(token="tok")


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_init_missing_token_raises(_env):
    with pytest.raises(ValueError, match="token"):
        OpenCTIConnector(url="https://octi.test")


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_filter_group_wraps_key_and_values_in_lists(_env):
    fg = OpenCTIConnector.filter_group("name", "Cobalt Strike")
    assert fg == {
        "mode": "and",
        "filters": [
            {"key": ["name"], "values": ["Cobalt Strike"], "operator": "eq", "mode": "or"}
        ],
        "filterGroups": [],
    }


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_filter_group_keeps_list_values(_env):
    fg = OpenCTIConnector.filter_group("entity_type", ["Malware", "Tool"], operator="eq")
    assert fg["filters"][0]["values"] == ["Malware", "Tool"]
    assert fg["filters"][0]["key"] == ["entity_type"]


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_list_entity_types(_env):
    c = OpenCTIConnector(url="https://octi.test", token="tok")
    assert c.list_entity_types() == q.SEARCHABLE_TYPES
    assert "Indicator" in c.list_entity_types()


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_search_entities_sends_query_and_returns_response(_env):
    c = OpenCTIConnector(url="https://octi.test", token="tok")
    captured = {}

    def fake_execute(query, variables=None, raise_on_errors=True):
        captured["query"] = query
        captured["vars"] = variables
        return _resp()

    c.execute = fake_execute
    result = c.search_entities(types=["Malware"], search="cobalt", first=5)
    assert isinstance(result, httpx.Response)
    assert captured["query"] == q.SEARCH_ENTITIES_QUERY
    assert captured["vars"]["types"] == ["Malware"]
    assert captured["vars"]["search"] == "cobalt"
    assert captured["vars"]["first"] == 5
    assert captured["vars"]["after"] is None


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_get_indicators_uses_indicator_query(_env):
    c = OpenCTIConnector(url="https://octi.test", token="tok")
    captured = {}

    def fake_execute(query, variables=None, raise_on_errors=True):
        captured["query"] = query
        captured["vars"] = variables
        return _resp()

    c.execute = fake_execute
    c.get_indicators(first=10)
    assert captured["query"] == q.INDICATORS_QUERY
    assert captured["vars"]["first"] == 10


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_get_relationships_normalizes_scalars_to_lists(_env):
    c = OpenCTIConnector(url="https://octi.test", token="tok")
    captured = {}

    def fake_execute(query, variables=None, raise_on_errors=True):
        captured["vars"] = variables
        return _resp()

    c.execute = fake_execute
    c.get_relationships(from_id="abc", relationship_type="uses")
    assert captured["vars"]["fromId"] == ["abc"]
    assert captured["vars"]["relationship_type"] == ["uses"]
    assert captured["vars"]["toId"] is None


@patch("pyapiary.api_connectors.opencti.combine_env_configs", return_value={})
def test_get_relationships_keeps_lists(_env):
    c = OpenCTIConnector(url="https://octi.test", token="tok")
    captured = {}

    def fake_execute(query, variables=None, raise_on_errors=True):
        captured["vars"] = variables
        return _resp()

    c.execute = fake_execute
    c.get_relationships(to_id=["x", "y"])
    assert captured["vars"]["toId"] == ["x", "y"]
    assert captured["vars"]["fromId"] is None
