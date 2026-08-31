import pytest
import vcr
from pathlib import Path

AUTH_PARAM_REDACT = [
    # List of substrings that, if present in a key, will cause redaction (case-insensitive)
    "key", "api_key", "access_token", "auth", "authorization", "user", "pass", "api", "x-api", "x_api", "token"
]


# Redact sensitive values from request body parameters
import json
def redact_sensitive(request):
    """Redact sensitive values from request body parameters."""
    if request.body:
        try:
            body = json.loads(request.body)
            for k in list(body.keys()):
                if any(redact_key.lower() in k.lower() for redact_key in AUTH_PARAM_REDACT):
                    body[k] = "REDACTED"
            request.body = json.dumps(body)
        except Exception:
            pass  # skip non-JSON or malformed bodies

    if request.headers:
        for k in list(request.headers.keys()):
            if any(redact_key.lower() in k.lower() for redact_key in AUTH_PARAM_REDACT):
                request.headers[k] = "REDACTED"

    return request


@pytest.fixture
def vcr_cassette(request):
    """Provides a VCR instance that stores cassettes in a test-local 'cassettes' folder."""
    test_dir = Path(request.module.__file__).parent
    cassette_dir = test_dir / "cassettes"

    config = {
        "cassette_library_dir": str(cassette_dir),
        "path_transformer": vcr.VCR.ensure_suffix(".yaml"),
        "record_mode": "once",
        "filter_headers": [("Authorization", "DUMMY")],
        "before_record": redact_sensitive
    }

    return vcr.VCR(**config)