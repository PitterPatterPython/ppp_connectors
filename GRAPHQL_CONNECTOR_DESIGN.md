# GraphQL Connector — Design Sketch (proposal, not yet implemented)

Status: **for discussion**. Nothing in `src/` is changed by this file.

## Decisions locked

1. **Return type:** `httpx.Response` everywhere — house law, no exceptions for request
   methods. (See "The Response-law reconciliation" for how GraphQL semantics fit inside that.)
2. **Mutations:** left open. The engine runs any document; access is governed by the
   permissions on the user's API token. To be documented in the README at implementation.
3. **Catalog:** ship what analysts actually do — *does X exist*, *what can I search*,
   *fetch + paginate entities*, *traverse relationships* — across observables, indicators,
   entities, threats, techniques, arsenal, locations. Bolt on more as needed.
4. **graphql-core:** yes — used to validate our shipped query catalog against a pinned
   SDL snapshot in CI, and optionally to validate bespoke queries at runtime.
5. **Async parity:** every class ships sync + async. House law.
6. **Catalog shape:** unified `search_entities(types=[...])` over `stixCoreObjects`, not
   named per-entity methods. `get_indicators` / `get_observables` stay dedicated only for
   their type-specific fields.
7. **No `exists()`.** No connector in the library synthesizes a derived value — they all
   return the underlying client's native object (`httpx.Response`, pymongo cursors/results,
   ES hits). An `exists() -> bool` would be the first exception, so it's dropped. The
   idiom is `search_entities(types=[...], filters=..., first=1)` then check `edges`
   (documented in the README).
8. **Type-specific fields = schema-driven, not pydantic.** GraphQL has no `SELECT *`, so the
   field list comes from the pinned SDL via `graphql-core` (emit all *leaf* scalar/enum
   fields per type). Default selection is core STIX fields; full per-type selection is
   opt-in. Same SDL artifact powers both query validation and field generation.

## The boundary

| Layer | Role | pyapiary analogy | Lives in |
|-------|------|------------------|----------|
| `GraphQLConnector` / `AsyncGraphQLConnector` | **Dumb executor.** Runs whatever query you give it. Knows nothing about OpenCTI. | DBMS connectors (`PostgresConnector.query`) | pyapiary `api_connectors/graphql.py` |
| `OpenCTIConnector` / `AsyncOpenCTIConnector` | **Thick, curated operations** with pre-composed queries. | REST connectors (`URLScanConnector.search`) | pyapiary `api_connectors/opencti.py` |
| Bespoke queries | One-off, app-specific. | hand-written SQL | the consuming app, via `execute()` |

DBMS-style interface (one generic `execute`), REST-style transport (HTTP via `Broker`).

---

## The Response-law reconciliation

Returning `httpx.Response` everywhere collides with two GraphQL realities. Here's how each is resolved without breaking the law:

- **Errors arrive as HTTP 200.** `execute()` still returns the `httpx.Response`. It *peeks*
  at the body only to decide whether to raise `GraphQLError`; on success it hands back the
  untouched Response. Cost: one internal `.json()` parse (the caller parses again — cheap,
  and consistent).
- **Pagination.** The connector does **not** paginate — exactly like `URLScanConnector.search`,
  which just passes `search_after` through `**kwargs` and returns the Response. We expose
  `after` as a normal passthrough arg; the caller reads `pageInfo.endCursor` from the body
  and calls again. Walking/accumulating pages is the caller's job, because doing it in the
  connector would mean parsing bodies and breaking the Response law.

With no `exists()` and no pagination helper, there are **zero** non-Response request methods.
Every method hands back the raw `httpx.Response`, matching every other API connector exactly.

---

## Layer 1 — `api_connectors/graphql.py` (the engine)

```python
import httpx
from typing import Dict, Any, Optional, List
from pyapiary.api_connectors.broker import (
    Broker, AsyncBroker, bubble_broker_init_signature, log_method_call,
)


class GraphQLError(Exception):
    """Raised when a GraphQL response carries a top-level `errors` array.
    Transport failures (4xx/5xx) still raise httpx.HTTPStatusError via Broker."""
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__("; ".join(e.get("message", str(e)) for e in errors))


@bubble_broker_init_signature()
class GraphQLConnector(Broker):
    """Generic, schema-agnostic GraphQL executor. Like the DBMS connectors,
    it does not care what your query is — it just runs it."""

    def __init__(self, base_url: str, endpoint: str = "/graphql", **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self.endpoint = endpoint

    @log_method_call
    def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        raise_on_errors: bool = True,
    ) -> httpx.Response:
        """POST a GraphQL document. Returns the httpx.Response (house law).
        Raises GraphQLError if the 200 body contains `errors` (unless disabled)."""
        resp = self.post(self.endpoint, json={"query": query, "variables": variables or {}})
        if raise_on_errors:
            body = resp.json()
            if body.get("errors"):
                raise GraphQLError(body["errors"])
        return resp


@bubble_broker_init_signature()
class AsyncGraphQLConnector(AsyncBroker):
    """Async twin of GraphQLConnector."""

    def __init__(self, base_url: str, endpoint: str = "/graphql", **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self.endpoint = endpoint

    @log_method_call
    async def execute(self, query, variables=None, raise_on_errors=True) -> httpx.Response:
        resp = await self.post(self.endpoint, json={"query": query, "variables": variables or {}})
        if raise_on_errors:
            body = resp.json()
            if body.get("errors"):
                raise GraphQLError(body["errors"])
        return resp
```

`log_method_call` already special-cases a `query` arg, so `execute` logs the query for free.
`Broker._make_request` already calls `raise_for_status()`, so transport failures are handled
upstream; we only add the GraphQL-200-error check.

---

## Layer 2 — OpenCTI catalog

### Design choice that shrinks the catalog

OpenCTI exposes a **universal root query, `stixCoreObjects`**, that returns *any* entity type,
filterable by `types: [String]`. That one query covers most of the analyst asks — threats,
arsenal, techniques, locations, entities — plus existence checks and pagination, uniformly.
So instead of ~25 near-duplicate methods (one per entity), the catalog is small:

| Method | Backing root query | Covers |
|--------|--------------------|--------|
| `search_entities(types=None, search=None, filters=None, ...)` | `stixCoreObjects` | threats, arsenal, techniques, locations, entities; free-text search; existence; pagination |
| `get_indicators(...)` | `indicators` | indicators (type-specific fields: pattern, score…) |
| `get_observables(...)` | `stixCyberObservables` | observables (type-specific: observable_value…) |
| `get_relationships(from_id=, to_id=, relationship_type=, ...)` | `stixCoreRelationships` | traversing relationships of anything |
| `exists(types, key, value)` | `stixCoreObjects` (first:1) | "does this entity exist?" |
| `list_entity_types()` / `SEARCHABLE_TYPES` | curated constant (+ optional `subTypes`) | "what can I search against?" |

`get_indicators` / `get_observables` exist as dedicated methods only because those two carry
heavily-used type-specific fields worth a tailored selection. Everything else rides
`search_entities`. Type-specific fields on `stixCoreObjects` come via inline fragments
(`... on Malware { is_family }`) added as analysts need them.

> VERIFIED against `docs/opencti-6.9.6.graphql` (introspected from the live instance):
> `stixCoreObjects(first, after, types, orderBy, orderMode, filters, search)`,
> `indicators(... toStix)`, `stixCyberObservables(... toStix)` all exist with these args.
> Both `threatActors` *and* `threatActorsGroup` exist (the former is the legacy field).
> `stixCoreRelationships` takes **list** args: `fromId/toId/relationship_type: [String]`,
> plus `fromTypes`, `toTypes`, `elementWithTargetTypes`, date ranges, `confidences`, etc.

### `api_connectors/opencti_queries.py` (the "shape" catalog)

```python
SEARCHABLE_TYPES = (
    "Stix-Cyber-Observable", "Indicator",
    "Threat-Actor", "Intrusion-Set", "Campaign",        # threats
    "Malware", "Tool", "Channel", "Vulnerability",       # arsenal
    "Attack-Pattern", "Narrative", "Course-Of-Action",   # techniques
    "Region", "Country", "City", "Position",             # locations
    "Individual", "Organization", "Sector", "System",    # entities
)

# VERIFIED 6.9.6: StixCoreObject is an INTERFACE whose only leaf fields are
# id, standard_id, entity_type, parent_types, created_at, updated_at, ... — there is
# NO `name` on the interface, so name/description MUST come via inline fragments per type.
SEARCH_ENTITIES_QUERY = """
query SearchEntities($types: [String], $search: String, $filters: FilterGroup,
                     $first: Int, $after: ID) {
  stixCoreObjects(types: $types, search: $search, filters: $filters,
                  first: $first, after: $after) {
    edges { node {
      id
      standard_id
      entity_type
      created_at
      updated_at
      ... on AttackPattern { name x_mitre_id }   # type-specific fragments
      ... on Malware { name is_family }
      ... on StixDomainObject { ... on Campaign { name } }
    } }
    pageInfo { endCursor hasNextPage globalCount }   # globalCount = total matches
  }
}
"""

INDICATORS_QUERY = """
query Indicators($filters: FilterGroup, $first: Int, $after: ID) {
  indicators(filters: $filters, first: $first, after: $after) {
    edges { node { id standard_id name pattern pattern_type
                   valid_from valid_until x_opencti_score confidence } }
    pageInfo { endCursor hasNextPage }
  }
}
"""
# OBSERVABLES_QUERY, RELATIONSHIPS_QUERY ... same shape.
```

### `api_connectors/opencti.py` (sync shown; async mirrors it, per house law)

```python
from typing import Dict, Any, Optional, List
import httpx
from pyapiary.api_connectors.graphql import GraphQLConnector
from pyapiary.api_connectors.broker import bubble_broker_init_signature, log_method_call
from pyapiary.helpers import combine_env_configs
from pyapiary.api_connectors import opencti_queries as q


@bubble_broker_init_signature()
class OpenCTIConnector(GraphQLConnector):
    """Curated operations for OpenCTI 6.9.x. Pinned to the schema snapshot
    in docs/opencti-6.9.6.graphql."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None, **kwargs):
        # OpenCTI instance URL is deployment-specific, so resolve url/token
        # eagerly from env here (unlike urlscan's hard-coded base_url).
        env = combine_env_configs()
        url = url or env.get("OPENCTI_URL")
        token = token or env.get("OPENCTI_TOKEN")
        if not url or not token:
            raise ValueError("OpenCTIConnector requires OPENCTI_URL and OPENCTI_TOKEN")
        super().__init__(base_url=url, endpoint="/graphql", **kwargs)
        self.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    @staticmethod
    def filter_group(key: str, values, operator: str = "eq", mode: str = "or") -> Dict[str, Any]:
        # VERIFIED against 6.9.6 schema: Filter.key is [String!]! and values is [Any!]!,
        # so both are wrapped in lists. operator ∈ FilterOperator (eq, not_eq, match,
        # wildcard, contains, starts_with, gt, lt, nil, search, ...); mode ∈ {and, or}.
        if not isinstance(values, list):
            values = [values]
        return {"mode": "and",
                "filters": [{"key": [key], "values": values, "operator": operator, "mode": mode}],
                "filterGroups": []}

    def list_entity_types(self) -> tuple:
        return q.SEARCHABLE_TYPES

    # --- request methods: return httpx.Response (house law) ------------------
    @log_method_call
    def search_entities(self, types: Optional[List[str]] = None, search: Optional[str] = None,
                        filters: Optional[Dict] = None, first: int = 100,
                        after: Optional[str] = None) -> httpx.Response:
        return self.execute(q.SEARCH_ENTITIES_QUERY,
                            {"types": types, "search": search, "filters": filters,
                             "first": first, "after": after})

    @log_method_call
    def get_indicators(self, filters=None, first=100, after=None) -> httpx.Response:
        return self.execute(q.INDICATORS_QUERY,
                            {"filters": filters, "first": first, "after": after})

    @log_method_call
    def get_relationships(self, from_id=None, to_id=None, relationship_type=None,
                          first=100, after=None) -> httpx.Response:
        return self.execute(q.RELATIONSHIPS_QUERY,
                            {"fromId": from_id, "toId": to_id,
                             "relationship_type": relationship_type,
                             "first": first, "after": after})

    # --- NO pagination helper: callers advance `after` themselves, exactly
    #     like urlscan's manual `search_after` (keeps the Response law intact).
    # --- NO exists(): use search_entities(..., first=1) and check edges.
    #     (No connector in the library returns a synthesized/derived value.)
```

Usage:

```python
with OpenCTIConnector() as octi:                       # env: OPENCTI_URL / OPENCTI_TOKEN

    # "does it exist?" idiom (no exists() method) — just first=1 + check edges
    flt = octi.filter_group("name", "Cobalt Strike")
    found = octi.search_entities(types=["Malware"], filters=flt, first=1) \
                .json()["data"]["stixCoreObjects"]["edges"]
    if found:

        # caller-driven pagination, same as urlscan's manual search_after loop
        resp = octi.search_entities(types=["Malware"], first=50)
        while True:
            page = resp.json()["data"]["stixCoreObjects"]
            for edge in page["edges"]:
                print(edge["node"]["entity_type"], edge["node"].get("name"))
            if not page["pageInfo"]["hasNextPage"]:
                break
            resp = octi.search_entities(types=["Malware"], first=50,
                                        after=page["pageInfo"]["endCursor"])

    octi.execute("query { me { name } }")              # bespoke escape hatch
```

---

## graphql-core: validating the shipped catalog (decision 4)

The point: catch schema drift in **our** query constants automatically, offline, in CI —
so when the OpenCTI version bumps, broken queries fail a test instead of a production call.

### 1. Generate the pinned SDL snapshot (once per version, done manually/ad hoc)

Run an introspection query against the instance (server must have
`APP__GRAPHQL__PLAYGROUND__FORCE_DISABLED_INTROSPECTION=false`), save the JSON to
`docs/opencti_schema.json` (gitignored), then convert it to committed SDL:

```python
import json
from graphql import build_client_schema, print_schema

data = json.load(open("docs/opencti_schema.json"))["data"]
schema = build_client_schema(data)
open("docs/opencti-6.9.6.graphql", "w").write(print_schema(schema))   # commit this
```

### 2. Validate every shipped query against the snapshot (CI test)

```python
# tests/test_opencti_queries.py
from pathlib import Path
import pytest
from graphql import build_schema, parse, validate
from pyapiary.api_connectors import opencti_queries as q

SCHEMA = build_schema(Path("docs/opencti-6.9.6.graphql").read_text())
QUERIES = {n: v for n, v in vars(q).items() if n.endswith("_QUERY") and isinstance(v, str)}

@pytest.mark.parametrize("name", QUERIES)
def test_shipped_query_matches_schema(name):
    errors = validate(SCHEMA, parse(QUERIES[name]))
    assert not errors, f"{name} drifted from schema: {[str(e) for e in errors]}"
```

`validate()` does full schema-aware checking — unknown fields, wrong arg types, bad
fragments — with **no live instance** needed in CI. Upgrade flow: re-run introspection
against the new version, regenerate the SDL (step 1), commit it, run the suite, fix
whatever turns red.

### 3. (Optional) runtime validation of bespoke queries

`GraphQLConnector(..., validate_against=<sdl str>)` could `validate()` a user's query before
sending, returning the GraphQL errors locally instead of round-tripping. Opt-in (requires
the user to supply an SDL), dev-dependency only.

---

## Schema-driven field selection (decision 8)

GraphQL has no `SELECT *`. To return type-specific fields without hand-maintaining fragments
or a pydantic model, generate the selection set from the pinned SDL with `graphql-core`:

```python
from graphql import build_schema, GraphQLScalarType, GraphQLEnumType, GraphQLNonNull, GraphQLList

def _unwrap(t):
    while isinstance(t, (GraphQLNonNull, GraphQLList)):
        t = t.of_type
    return t

def scalar_fields(schema, type_name: str) -> list[str]:
    """All leaf (scalar/enum) fields of a type — straight from the schema."""
    t = schema.get_type(type_name)
    return [name for name, f in t.fields.items()
            if isinstance(_unwrap(f.type), (GraphQLScalarType, GraphQLEnumType))]

def inline_fragment(schema, type_name: str) -> str:
    return f"... on {type_name} {{ {' '.join(scalar_fields(schema, type_name))} }}"
```

- **Default selection:** core STIX fields (`id`, `standard_id`, `entity_type`, …) — cheap,
  type-agnostic, covers most use cases.
- **Full per-type selection:** opt-in (e.g. a `fields="all"` mode), which expands the
  requested `types` into generated `inline_fragment(...)` blocks. Only *leaf* fields are
  emitted — object/relationship fields would recurse, so they're excluded (or nested as
  `{ id }`).
- Generated queries are still CI-validated: generate per type, run `validate()` against the
  SDL just like the static ones.

## Status: design complete + schema captured

All eight decisions locked, and the design is now verified against the live 6.9.6 schema.

Schema artifacts already in the repo (introspection requires the server's
`APP__GRAPHQL__PLAYGROUND__FORCE_DISABLED_INTROSPECTION=false`, toggled on temporarily):
- `docs/opencti_schema.json` — raw introspection result (3.4 MB, 1041 types).
- `docs/opencti-6.9.6.graphql` — readable SDL (the authoring/validation reference).

Implementation order when ready:

1. `api_connectors/graphql.py` — `GraphQLConnector` + `AsyncGraphQLConnector` + `GraphQLError`.
2. ~~dump schema~~ — DONE (artifacts above).
3. `api_connectors/opencti_queries.py` — query constants + `scalar_fields`/`inline_fragment`,
   generated from `docs/opencti-6.9.6.graphql`.
4. `api_connectors/opencti.py` — `OpenCTIConnector` + `AsyncOpenCTIConnector`.
5. Wire exports in `pyapiary/__init__.py`.
6. Tests: shipped-query validation (graphql-core, offline against the committed SDL) +
   VCR cassettes for live calls.
7. README: auth/env vars, token-permission note (mutations), the `first=1` existence idiom.
