import httpx
from typing import Any, Dict, List, Optional
from pyapiary.api_connectors.broker import (
    Broker,
    AsyncBroker,
    bubble_broker_init_signature,
    log_method_call,
)


class GraphQLError(Exception):
    """Raised when a GraphQL response returns a top-level ``errors`` array.

    GraphQL returns HTTP 200 even when a query fails, so ``raise_for_status``
    (already applied by Broker) never catches these. This exception surfaces
    those query-level errors. Transport failures (4xx/5xx) still raise
    ``httpx.HTTPStatusError`` from Broker as usual.

    Attributes:
        errors (List[Dict[str, Any]]): The raw ``errors`` array from the response.
    """

    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__("; ".join(e.get("message", str(e)) for e in errors))


@bubble_broker_init_signature()
class GraphQLConnector(Broker):
    """A generic, schema-agnostic GraphQL executor.

    Like the DBMS connectors, this connector does not know or care what your
    query is -- it just runs it. Point it at any GraphQL endpoint. Built on
    ``Broker``, so it inherits retries, proxy handling, timeouts, logging, and
    optional environment config loading.

    Attributes:
        endpoint (str): Path appended to ``base_url`` for GraphQL requests.
    """

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
        """Execute a GraphQL document and return the raw ``httpx.Response``.

        Args:
            query (str): The GraphQL query or mutation document.
            variables (Optional[Dict[str, Any]]): GraphQL variables.
            raise_on_errors (bool): If True (default), raise ``GraphQLError``
                when the 200 response body contains an ``errors`` array. Set
                False to let the caller inspect ``response.json()["errors"]``.

        Returns:
            httpx.Response: The raw response object (house convention).

        Raises:
            GraphQLError: When ``raise_on_errors`` and the body has ``errors``.
            httpx.HTTPStatusError: On transport-level failures (via Broker).
        """
        resp = self.post(self.endpoint, json={"query": query, "variables": variables or {}})
        if raise_on_errors:
            body = resp.json()
            if body.get("errors"):
                raise GraphQLError(body["errors"])
        return resp


@bubble_broker_init_signature()
class AsyncGraphQLConnector(AsyncBroker):
    """Async version of :class:`GraphQLConnector` using ``AsyncBroker``."""

    def __init__(self, base_url: str, endpoint: str = "/graphql", **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self.endpoint = endpoint

    @log_method_call
    async def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        raise_on_errors: bool = True,
    ) -> httpx.Response:
        """Async execute a GraphQL document. See :meth:`GraphQLConnector.execute`."""
        resp = await self.post(self.endpoint, json={"query": query, "variables": variables or {}})
        if raise_on_errors:
            body = resp.json()
            if body.get("errors"):
                raise GraphQLError(body["errors"])
        return resp
