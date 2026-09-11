from elasticsearch import Elasticsearch, NotFoundError, helpers
from typing import List, Dict, Generator, Any, Optional, Union


try:
    from pyapiary.helpers import setup_logger
    _default_logger = setup_logger(name="elasticsearch")
except ImportError:
    import logging
    _default_logger = logging.getLogger("elasticsearch")
    if not _default_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        _default_logger.addHandler(handler)
    _default_logger.setLevel(logging.INFO)


_SEARCH_BODY_KEYS = frozenset({
    "aggregations", "aggs", "collapse", "docvalue_fields", "explain", "ext",
    "fields", "from", "highlight", "indices_boost", "knn", "min_score", "pit",
    "post_filter", "profile", "query", "rescore", "retriever", "runtime_mappings",
    "script_fields", "search_after", "seq_no_primary_term", "size", "slice",
    "sort", "_source", "stats", "stored_fields", "suggest", "terminate_after",
    "timeout", "track_scores", "track_total_hits", "version",
})


class ElasticsearchConnector:
    """
    A connector class for interacting with Elasticsearch.

    This class provides methods to perform paginated search queries using the scroll API
    and to execute bulk insert operations. It includes integrated logging support for observability.
    """
    def __init__(
        self,
        hosts: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[Union[str, tuple]] = None,
        verify_certs: bool = True,
        ca_certs: Optional[str] = None,
        request_timeout: Optional[float] = None,
        logger: Optional[Any] = None,
        **client_kwargs: Any
    ):
        """
        Initialize the Elasticsearch client.

        Args:
            hosts (List[str]): List of Elasticsearch host URLs. Each entry must include a
                scheme, host and port (e.g. "https://localhost:9200").
            username (Optional[str]): Username for basic authentication. Defaults to None.
            password (Optional[str]): Password for basic authentication. Defaults to None.
            api_key (Optional[Union[str, tuple]]): API key for authentication, as either an
                encoded string or an (id, api_key) tuple. Mutually exclusive with
                username/password. Defaults to None.
            verify_certs (bool): Whether to verify TLS certificates. Defaults to True.
            ca_certs (Optional[str]): Path to a CA bundle used to verify the cluster's
                certificate. Defaults to None.
            request_timeout (Optional[float]): Per-request timeout in seconds. Defaults to
                None, which uses the client default.
            logger (Optional[Any]): Optional logger instance. If not provided, a default logger is used.
            **client_kwargs (Any): Additional keyword arguments passed through to
                ``Elasticsearch`` (e.g. ``retry_on_timeout``, ``max_retries``).

        Raises:
            ValueError: If both basic auth credentials and an API key are supplied, or if
                only one of username/password is supplied.
        """
        self.logger = logger if logger is not None else _default_logger

        if username is not None or password is not None:
            if api_key is not None:
                raise ValueError("Provide either username/password or api_key, not both")
            if username is None or password is None:
                raise ValueError("Both username and password are required for basic auth")
            client_kwargs["basic_auth"] = (username, password)
        elif api_key is not None:
            client_kwargs["api_key"] = api_key

        if not verify_certs:
            client_kwargs["verify_certs"] = False
        if ca_certs is not None:
            client_kwargs["ca_certs"] = ca_certs
        if request_timeout is not None:
            client_kwargs["request_timeout"] = request_timeout

        self.client = Elasticsearch(hosts, **client_kwargs)

    def _log(self, msg: str, level: str = "info"):
        """
        Internal helper to log messages using the provided or default logger.

        Args:
            msg (str): The message to log.
            level (str): The logging level as a string (e.g., 'info', 'error'). Defaults to 'info'.
        """
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(msg)

    @staticmethod
    def _build_search_body(query: Union[str, Dict]) -> Dict[str, Any]:
        """
        Normalize the supported query forms into a full Elasticsearch search body.

        Three forms are accepted:
          * a Lucene query string, wrapped into a ``query_string`` clause;
          * a complete search body, e.g. ``{"query": {...}, "sort": [...]}``, used as-is;
          * a bare query clause, e.g. ``{"match_all": {}}``, wrapped into ``{"query": ...}``.

        Args:
            query (Union[str, Dict]): The query in any of the supported forms.

        Returns:
            Dict[str, Any]: A search body suitable for the ``_search`` endpoint.

        Raises:
            TypeError: If query is neither a string nor a dictionary.
        """
        if isinstance(query, str):
            return {"query": {"query_string": {"query": query}}}
        if not isinstance(query, dict):
            raise TypeError(
                f"query must be a Lucene string or a dict, got {type(query).__name__}"
            )
        if not query:
            return {"query": {"match_all": {}}}
        if set(query).issubset(_SEARCH_BODY_KEYS):
            return dict(query)
        return {"query": dict(query)}

    def query(
        self,
        index: str,
        query: Union[str, Dict],
        size: int = 1000,
        scroll: str = "5m"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a paginated search query using the Elasticsearch scroll API.

        This method handles retrieval of large result sets by paging through results
        using a scroll context. The scroll context is released when the generator is
        exhausted, closed, or garbage collected.

        Args:
            index (str): The name of the index to search.
            query (Union[str, Dict]): A Lucene query string, a full Elasticsearch DSL search
                body (``{"query": {...}}``), or a bare query clause (``{"match_all": {}}``).
            size (int): Number of results to retrieve per batch. Ignored if the search body
                already specifies "size". Defaults to 1000.
            scroll (str): How long each scroll context is kept alive between batches. Raise
                this if downstream processing of a batch is slow. Defaults to "5m".

        Yields:
            Generator[Dict[str, Any], None, None]: A generator that yields each search hit as a dictionary.

        Note:
            This method returns a generator. If you want to collect all results,
            you can wrap the result in `list()`, but beware of memory usage if the
            result set is large. Prefer streaming and processing results incrementally.
        """
        body = self._build_search_body(query)
        body.setdefault("size", size)

        self._log(
            f"Executing query on index '{index}' with batch size {body['size']}", "info"
        )

        try:
            page = self.client.search(index=index, body=body, scroll=scroll)
        except NotFoundError:
            self._log(
                f"Index '{index}' was not found on the cluster; check the index name, "
                f"any alias or wildcard it should match, and that the credentials in use "
                f"are allowed to read it",
                "error"
            )
            raise

        sid = page.get("_scroll_id")
        hits = page["hits"]["hits"]
        if sid is None:
            self._log(
                f"Cluster returned no scroll id for index '{index}'; yielding the first "
                f"page only. Scroll is unavailable on Elasticsearch Serverless",
                "warning"
            )
            yield from hits
            return

        total = 0
        try:
            while hits:
                yield from hits
                total += len(hits)
                try:
                    page = self.client.scroll(scroll_id=sid, scroll=scroll)
                except NotFoundError:
                    self._log(
                        f"Scroll context expired after {total} hits from index '{index}'; "
                        f"processing a batch took longer than the scroll TTL of {scroll}. "
                        f"Raise the 'scroll' argument or lower 'size'",
                        "error"
                    )
                    raise
                sid = page.get("_scroll_id", sid)
                hits = page["hits"]["hits"]
        finally:
            self.client.options(ignore_status=404).clear_scroll(scroll_id=sid)

        self._log(
            f"Completed scrolling query on index '{index}', yielded {total} hits", "info"
        )

    def bulk_insert(
        self,
        index: str,
        data: List[Dict],
        id_key: str = "_id",
        chunk_size: int = 500,
        raise_on_error: bool = False
    ):
        """
        Perform a bulk insert operation into the specified Elasticsearch index.

        This method sends batches of documents for indexing in a single API call.
        Each document can optionally specify an ID via the `id_key`; documents without
        that key are indexed with a cluster-generated ID.

        Args:
            index (str): The name of the index to insert documents into.
            data (List[Dict]): A list of documents to insert.
            id_key (str): The key in each document to use as the document ID. Defaults to "_id".
            chunk_size (int): Number of documents sent per bulk request. Defaults to 500.
            raise_on_error (bool): If True, raise ``BulkIndexError`` on the first failed
                document instead of collecting failures. Defaults to False.

        Returns:
            Tuple[int, List[Dict]]: A tuple containing the number of successfully processed actions
                                    and a list of any errors encountered during insertion.
        """
        self._log(f"Inserting {len(data)} documents into index '{index}'", "info")
        actions = []
        for doc in data:
            action = {"_index": index, "_source": doc}
            doc_id = doc.get(id_key)
            if doc_id is not None:
                action["_id"] = doc_id
            actions.append(action)

        success, errors = helpers.bulk(
            self.client,
            actions,
            chunk_size=chunk_size,
            raise_on_error=raise_on_error,
        )
        if errors:
            self._log(f"Bulk insert encountered errors: {errors}", "error")
        else:
            self._log("Bulk insert completed successfully", "info")
        return success, errors
