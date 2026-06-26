"""Offline validation of the shipped OpenCTI query catalog against the pinned SDL.

This catches schema drift in our own query constants when OpenCTI changes
versions: regenerate docs/opencti-<version>.graphql, run this suite, and any
query referencing a renamed/removed field or bad arg type fails here -- not in
production. No live OpenCTI instance is needed.
"""
from pathlib import Path
import pytest

from pyapiary.api_connectors import opencti_queries as q

# graphql-core is a dev dependency; skip cleanly if unavailable.
graphql = pytest.importorskip("graphql")
from graphql import build_schema, parse, validate  # noqa: E402


def _find_sdl() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "opencti-6.9.6.graphql"
        if candidate.exists():
            return candidate
    return None


SDL_PATH = _find_sdl()

SHIPPED_QUERIES = {
    name: getattr(q, name)
    for name in dir(q)
    if name.endswith("_QUERY") and isinstance(getattr(q, name), str)
}


def test_catalog_has_queries():
    assert SHIPPED_QUERIES, "no *_QUERY constants found in opencti_queries"


@pytest.mark.skipif(SDL_PATH is None, reason="docs/opencti-6.9.6.graphql snapshot not present")
@pytest.mark.parametrize("name", sorted(SHIPPED_QUERIES))
def test_shipped_query_matches_schema(name):
    schema = build_schema(SDL_PATH.read_text())
    errors = validate(schema, parse(SHIPPED_QUERIES[name]))
    assert not errors, f"{name} drifted from schema: {[e.message for e in errors]}"
