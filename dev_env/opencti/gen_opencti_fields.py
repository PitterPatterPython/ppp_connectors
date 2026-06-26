#!/usr/bin/env python3
"""Dev helper: generate GraphQL field selections from the pinned OpenCTI SDL.

This is a *development-time* tool, NOT imported by the library at runtime (so
the runtime stays dependency-free apart from httpx). Use it to author or expand
the static query field lists in ``pyapiary.api_connectors.opencti_queries``
without hand-maintaining them or marrying to a pydantic model -- the SDL is the
source of truth.

GraphQL has no ``SELECT *``; this emits all *leaf* (scalar/enum) fields of a
type. Object/relationship fields are skipped (they would recurse); add those by
hand where you need them.

Usage:
    pip install graphql-core
    python dev_env/opencti/gen_opencti_fields.py Indicator
    python dev_env/opencti/gen_opencti_fields.py Malware --fragment
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from graphql import build_schema
from graphql.type import GraphQLEnumType, GraphQLScalarType


def _find_sdl() -> Path | None:
    """Walk up from this file to find docs/opencti-6.9.6.graphql."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "opencti-6.9.6.graphql"
        if candidate.exists():
            return candidate
    return None


def _unwrap(t):
    while hasattr(t, "of_type"):
        t = t.of_type
    return t


def scalar_fields(schema, type_name: str) -> list[str]:
    """All leaf (scalar/enum) field names of a type, straight from the schema."""
    t = schema.type_map.get(type_name)
    if t is None or not hasattr(t, "fields"):
        raise SystemExit(f"Type not found or has no fields: {type_name}")
    return [
        name
        for name, f in t.fields.items()
        if isinstance(_unwrap(f.type), (GraphQLScalarType, GraphQLEnumType))
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("type_name", help="GraphQL type name, e.g. Indicator")
    ap.add_argument("--fragment", action="store_true",
                    help="wrap as an inline fragment: '... on Type { ... }'")
    ap.add_argument("--sdl", default=None, help="path to SDL file (auto-detected by default)")
    args = ap.parse_args()

    sdl_path = Path(args.sdl) if args.sdl else _find_sdl()
    if sdl_path is None or not sdl_path.exists():
        raise SystemExit("Could not find docs/opencti-6.9.6.graphql; pass --sdl explicitly.")

    schema = build_schema(sdl_path.read_text())
    fields = scalar_fields(schema, args.type_name)
    body = " ".join(fields)
    if args.fragment:
        print(f"... on {args.type_name} {{ {body} }}")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
