import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(".env.test")

@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://mock.proxy")
    monkeypatch.setenv("HTTPS_PROXY", "https://mock.proxy")
    monkeypatch.setenv("VERIFY_SSL", "False")
    monkeypatch.setenv("SPYCLOUD_API_ATO_KEY", "mock_ato_key")
    monkeypatch.setenv("SPYCLOUD_API_SIP_KEY", "mock_sip_key")