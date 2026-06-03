import httpx
from typing import Optional
from pyapiary.api_connectors.broker import Broker, AsyncBroker, bubble_broker_init_signature, log_method_call

@bubble_broker_init_signature()
class FlashpointConnector(Broker):
    """
    FlashpointConnector provides access to various Flashpoint API search and retrieval endpoints
    using a consistent Broker-based interface.

    Attributes:
        api_key (str): Flashpoint API token used for bearer authentication.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.flashpoint.io", **kwargs)
        self.api_key = api_key or self.env_config.get("FLASHPOINT_API_KEY")
        if not self.api_key:
            raise ValueError("FLASHPOINT_API_KEY is required")
        self.headers.update({
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })

    @log_method_call
    def search_communities(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint communities data.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return self.post("/sources/v2/communities", json={"query": query, **kwargs})

    @log_method_call
    def search_fraud(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint fraud datasets.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return self.post("/sources/v2/fraud", json={"query": query, **kwargs})

    @log_method_call
    def search_fraud_checks(self, query: str, **kwargs) -> httpx.Response:
        """Checks search provides the ability to search and read data from our Checks dataset.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return self.post("/sources/v2/fraud/checks", json={"query": query, **kwargs})

    @log_method_call
    def search_marketplaces(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint marketplace datasets.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return self.post("/sources/v2/markets", json={"query": query, **kwargs})

    @log_method_call
    def search_media(self, query: str, **kwargs) -> httpx.Response:
        """
        Search OCR-processed media from Flashpoint.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return self.post("/sources/v2/media", json={"query": query, **kwargs})

    @log_method_call
    def get_media_object(self, query: str, **kwargs) -> httpx.Response:
        """
        Retrieve metadata for a specific media object.

        Args:
            query (str): The media_id of the object to retrieve.
            **kwargs: Additional request options.
        """
        return self.get(f"/sources/v2/media/{query}")

    @log_method_call
    def get_media_image(self, query: str, **kwargs) -> httpx.Response:
        """
        Download image asset by storage_uri.

        Args:
            query (str): The storage_uri (asset_id) of the image to download.
            **kwargs: Additional request options.
        """
        safe_headers = {"Authorization": f"Bearer {self.api_key}"}
        return self.get("/sources/v1/media/", headers=safe_headers, params={"asset_id": query})

    @log_method_call
    def search_checks(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint fraud check datasets.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return self.post("/sources/v2/fraud/checks", json={"query": query, **kwargs})


# Async version of FlashpointConnector
@bubble_broker_init_signature()
class AsyncFlashpointConnector(AsyncBroker):
    """
    AsyncFlashpointConnector provides async access to Flashpoint API endpoints.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.flashpoint.io", **kwargs)
        self.api_key = api_key or self.env_config.get("FLASHPOINT_API_KEY")
        if not self.api_key:
            raise ValueError("FLASHPOINT_API_KEY is required")
        self.headers.update({
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })

    @log_method_call
    async def search_communities(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint communities data.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return await self.post("/sources/v2/communities", json={"query": query, **kwargs})

    @log_method_call
    async def search_fraud(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint fraud datasets.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return await self.post("/sources/v2/fraud", json={"query": query, **kwargs})

    @log_method_call
    async def search_fraud_checks(self, query: str, **kwargs) -> httpx.Response:
        """Checks search provides the ability to search and read data from our Checks dataset.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return await self.post("/sources/v2/fraud/checks", json={"query": query, **kwargs})

    @log_method_call
    async def search_marketplaces(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint marketplace datasets.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return await self.post("/sources/v2/markets", json={"query": query, **kwargs})

    @log_method_call
    async def search_media(self, query: str, **kwargs) -> httpx.Response:
        """
        Search OCR-processed media from Flashpoint.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return await self.post("/sources/v2/media", json={"query": query, **kwargs})

    @log_method_call
    async def get_media_object(self, query: str) -> httpx.Response:
        """
        Retrieve metadata for a specific media object.

        Args:
            query (str): The media_id of the object to retrieve.
        """
        return await self.get(f"/sources/v2/media/{query}")

    @log_method_call
    async def get_media_image(self, query: str) -> httpx.Response:
        """
        Download image asset by storage_uri.

        Args:
            query (str): The storage_uri (asset_id) of the image to download.
        """
        safe_headers = {"Authorization": f"Bearer {self.api_key}"}
        return await self.get("/sources/v1/media/", headers=safe_headers, params={"asset_id": query})

    @log_method_call
    async def search_checks(self, query: str, **kwargs) -> httpx.Response:
        """
        Search Flashpoint fraud check datasets asynchronously.

        Args:
            query (str): The search string used in the API query.
            **kwargs: Additional query logic per the Flashpoint API documentation.
        """
        return await self.post("/sources/v2/fraud/checks", json={"query": query, **kwargs})