import asyncio
import httpx
from pyapiary.api_connectors.flashpoint import FlashpointConnector, AsyncFlashpointConnector

fp = AsyncFlashpointConnector(
    load_env_vars=True,
    trust_env=True,
    verify=False,
    follow_redirects=True
)

async def main():
    # Insert test here
    pass

asyncio.run(main())