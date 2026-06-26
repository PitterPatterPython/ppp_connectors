import httpx
from typing import Any, Dict, List, Optional, Union
from pyapiary.api_connectors.graphql import GraphQLConnector, AsyncGraphQLConnector
from pyapiary.api_connectors.broker import bubble_broker_init_signature, log_method_call
from pyapiary.helpers import combine_env_configs
from pyapiary.api_connectors import opencti_queries as q


def _as_list(value: Optional[Union[str, List[str]]]) -> Optional[List[str]]:
    """Normalize a scalar/list value to a list (or None) for list-typed args."""
    if value is None:
        return None
    return value if isinstance(value, list) else [value]


def _build_filter_group(key: str, values, operator: str = "eq", mode: str = "or") -> Dict[str, Any]:
    """Build an OpenCTI 6.9.x FilterGroup for a single key/value(s) filter.

    Verified against the 6.9.6 schema: ``Filter.key`` is ``[String!]!`` and
    ``values`` is ``[Any!]!`` (both lists).

    Args:
        key (str): The field key to filter on (e.g. "name", "entity_type").
        values: A single value or list of values to match.
        operator (str): A FilterOperator (eq, not_eq, match, wildcard, contains,
            starts_with, gt, lt, nil, search, ...). Defaults to "eq".
        mode (str): "and" or "or" within this filter's values. Defaults to "or".

    Returns:
        Dict[str, Any]: A FilterGroup dict ready to pass as the ``filters`` arg.
    """
    if not isinstance(values, list):
        values = [values]
    return {
        "mode": "and",
        "filters": [{"key": [key], "values": values, "operator": operator, "mode": mode}],
        "filterGroups": [],
    }


@bubble_broker_init_signature()
class OpenCTIConnector(GraphQLConnector):
    """Curated operations for OpenCTI 6.9.x over its GraphQL API.

    A thick connector (urlscan-style) on top of the generic GraphQLConnector.
    Query field selections are pinned to the schema captured in
    ``docs/opencti-6.9.6.graphql``. For anything outside the curated catalog,
    use the inherited :meth:`execute` directly with your own query.

    Credentials are read from ``OPENCTI_URL`` and ``OPENCTI_TOKEN`` (or passed
    explicitly). Access is governed by the permissions on the token's user.

    Attributes:
        token (str): The API token used for Bearer auth.
    """

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None, **kwargs):
        # The OpenCTI instance URL is deployment-specific, so resolve url/token
        # eagerly from env here (Broker's env_config is only populated after
        # super().__init__, but we need the url to call it).
        env = combine_env_configs()
        url = url or env.get("OPENCTI_URL")
        token = token or env.get("OPENCTI_TOKEN")
        if not url:
            raise ValueError("OpenCTIConnector requires a url (or OPENCTI_URL env var)")
        if not token:
            raise ValueError("OpenCTIConnector requires a token (or OPENCTI_TOKEN env var)")

        super().__init__(base_url=url, endpoint="/graphql", **kwargs)
        self.token = token
        self.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    # --- helpers -------------------------------------------------------------
    @staticmethod
    def filter_group(key: str, values, operator: str = "eq", mode: str = "or") -> Dict[str, Any]:
        """Build an OpenCTI FilterGroup. See :func:`_build_filter_group`."""
        return _build_filter_group(key, values, operator=operator, mode=mode)

    @log_method_call
    def list_entity_types(self) -> tuple:
        """Return the curated tuple of searchable OpenCTI entity types."""
        return q.SEARCHABLE_TYPES

    # --- request methods: return httpx.Response (house convention) -----------
    @log_method_call
    def search_entities(
        self,
        types: Optional[List[str]] = None,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Search/list STIX core objects of any type (threats, arsenal,
        techniques, locations, entities, ...). Paginate by passing ``after``
        with the previous page's ``pageInfo.endCursor``.

        Returns:
            httpx.Response: ``data.stixCoreObjects`` connection in the body.
        """
        return self.execute(
            q.SEARCH_ENTITIES_QUERY,
            {"types": types, "search": search, "filters": filters, "first": first, "after": after},
        )

    @log_method_call
    def get_indicators(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Fetch indicators with indicator-specific fields (pattern, score, ...)."""
        return self.execute(
            q.INDICATORS_QUERY,
            {"filters": filters, "search": search, "first": first, "after": after},
        )

    @log_method_call
    def get_observables(
        self,
        types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Fetch STIX cyber observables (observable_value, score, ...)."""
        return self.execute(
            q.OBSERVABLES_QUERY,
            {"types": types, "filters": filters, "search": search, "first": first, "after": after},
        )

    @log_method_call
    def get_relationships(
        self,
        from_id: Optional[Union[str, List[str]]] = None,
        to_id: Optional[Union[str, List[str]]] = None,
        relationship_type: Optional[Union[str, List[str]]] = None,
        filters: Optional[Dict[str, Any]] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Traverse STIX core relationships. ``from_id``/``to_id``/
        ``relationship_type`` accept a single value or a list (the schema args
        are ``[String]``)."""
        return self.execute(
            q.RELATIONSHIPS_QUERY,
            {
                "fromId": _as_list(from_id),
                "toId": _as_list(to_id),
                "relationship_type": _as_list(relationship_type),
                "filters": filters,
                "first": first,
                "after": after,
            },
        )


@bubble_broker_init_signature()
class AsyncOpenCTIConnector(AsyncGraphQLConnector):
    """Async version of :class:`OpenCTIConnector`."""

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None, **kwargs):
        env = combine_env_configs()
        url = url or env.get("OPENCTI_URL")
        token = token or env.get("OPENCTI_TOKEN")
        if not url:
            raise ValueError("AsyncOpenCTIConnector requires a url (or OPENCTI_URL env var)")
        if not token:
            raise ValueError("AsyncOpenCTIConnector requires a token (or OPENCTI_TOKEN env var)")

        super().__init__(base_url=url, endpoint="/graphql", **kwargs)
        self.token = token
        self.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    @staticmethod
    def filter_group(key: str, values, operator: str = "eq", mode: str = "or") -> Dict[str, Any]:
        """Build an OpenCTI FilterGroup. See :func:`_build_filter_group`."""
        return _build_filter_group(key, values, operator=operator, mode=mode)

    @log_method_call
    def list_entity_types(self) -> tuple:
        """Return the curated tuple of searchable OpenCTI entity types."""
        return q.SEARCHABLE_TYPES

    @log_method_call
    async def search_entities(
        self,
        types: Optional[List[str]] = None,
        search: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Async search/list STIX core objects. See :meth:`OpenCTIConnector.search_entities`."""
        return await self.execute(
            q.SEARCH_ENTITIES_QUERY,
            {"types": types, "search": search, "filters": filters, "first": first, "after": after},
        )

    @log_method_call
    async def get_indicators(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Async fetch indicators. See :meth:`OpenCTIConnector.get_indicators`."""
        return await self.execute(
            q.INDICATORS_QUERY,
            {"filters": filters, "search": search, "first": first, "after": after},
        )

    @log_method_call
    async def get_observables(
        self,
        types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Async fetch observables. See :meth:`OpenCTIConnector.get_observables`."""
        return await self.execute(
            q.OBSERVABLES_QUERY,
            {"types": types, "filters": filters, "search": search, "first": first, "after": after},
        )

    @log_method_call
    async def get_relationships(
        self,
        from_id: Optional[Union[str, List[str]]] = None,
        to_id: Optional[Union[str, List[str]]] = None,
        relationship_type: Optional[Union[str, List[str]]] = None,
        filters: Optional[Dict[str, Any]] = None,
        first: int = 100,
        after: Optional[str] = None,
    ) -> httpx.Response:
        """Async traverse relationships. See :meth:`OpenCTIConnector.get_relationships`."""
        return await self.execute(
            q.RELATIONSHIPS_QUERY,
            {
                "fromId": _as_list(from_id),
                "toId": _as_list(to_id),
                "relationship_type": _as_list(relationship_type),
                "filters": filters,
                "first": first,
                "after": after,
            },
        )
