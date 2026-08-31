import httpx
import pytest
from pyapiary.api_connectors.spur import SpurConnector

@pytest.mark.integration
def test_spur_context_vcr(vcr_cassette):
    with vcr_cassette.use_cassette("test_spur_context_vcr"):
        connector = SpurConnector(load_env_vars=True)
        result = connector.context("1.1.1.1")
        assert isinstance(result, httpx.Response)
        assert "ip" in result.json()
