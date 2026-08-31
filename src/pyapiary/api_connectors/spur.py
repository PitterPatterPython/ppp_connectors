import httpx
from typing import Optional
from pyapiary.api_connectors.broker import Broker, AsyncBroker, bubble_broker_init_signature, log_method_call


@bubble_broker_init_signature()
class SpurConnector(Broker):
    """
    SpurConnector provides access to the Spur Context API for IP intelligence
    lookups using a consistent Broker-based interface.

    Attributes:
        api_key (str): Spur API token used for Token-header authentication.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.spur.us", **kwargs)
        self.api_key = api_key or self.env_config.get("SPUR_API_KEY")
        if not self.api_key:
            raise ValueError("SPUR_API_KEY is required")
        self.headers.update({
            "accept": "application/json",
            "Token": self.api_key,
        })

    @log_method_call
    def context(self, query: str, **kwargs) -> httpx.Response:
        """
        Look up Context API data for an IP address.

        Args:
            query (str): The IPv4 or IPv6 address to look up.
            **kwargs: Additional query parameters, e.g. mmgeo=1 to include MaxMind
                geolocation data, or dt=YYYYmmdd for historical context (Enterprise
                plans only).
        """
        return self.get(f"/v2/context/{query}", params=kwargs)

    @log_method_call
    def tag_metadata(self, query: str, **kwargs) -> httpx.Response:
        """
        Retrieve metadata describing a Spur service tag.

        Args:
            query (str): The service tag identifier.
            **kwargs: Additional query parameters per the Spur API documentation.
        """
        return self.get(f"/v2/metadata/tags/{query}", params=kwargs)

    @log_method_call
    def status(self, **kwargs) -> httpx.Response:
        """
        Check the API token's status, including remaining query balance and
        service tier.

        Args:
            **kwargs: Additional query parameters per the Spur API documentation.
        """
        return self.get("/status", params=kwargs)


# Async version of SpurConnector
@bubble_broker_init_signature()
class AsyncSpurConnector(AsyncBroker):
    """
    AsyncSpurConnector provides async access to Spur Context API endpoints.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(base_url="https://api.spur.us", **kwargs)
        self.api_key = api_key or self.env_config.get("SPUR_API_KEY")
        if not self.api_key:
            raise ValueError("SPUR_API_KEY is required")
        self.headers.update({
            "accept": "application/json",
            "Token": self.api_key,
        })

    @log_method_call
    async def context(self, query: str, **kwargs) -> httpx.Response:
        """
        Look up Context API data for an IP address.

        Args:
            query (str): The IPv4 or IPv6 address to look up.
            **kwargs: Additional query parameters, e.g. mmgeo=1 to include MaxMind
                geolocation data, or dt=YYYYmmdd for historical context (Enterprise
                plans only).
        """
        return await self.get(f"/v2/context/{query}", params=kwargs)

    @log_method_call
    async def tag_metadata(self, query: str, **kwargs) -> httpx.Response:
        """
        Retrieve metadata describing a Spur service tag.

        Args:
            query (str): The service tag identifier.
            **kwargs: Additional query parameters per the Spur API documentation.
        """
        return await self.get(f"/v2/metadata/tags/{query}", params=kwargs)

    @log_method_call
    async def status(self, **kwargs) -> httpx.Response:
        """
        Check the API token's status, including remaining query balance and
        service tier.

        Args:
            **kwargs: Additional query parameters per the Spur API documentation.
        """
        return await self.get("/status", params=kwargs)
