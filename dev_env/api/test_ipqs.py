from pyapiary.api_connectors.ipqs import AsyncIPQSConnector, IPQSConnector
import asyncio
from pyapiary.helpers import combine_env_configs, setup_logger
from typing import Dict, Any
import json


env_config: Dict[str, Any] = combine_env_configs()

async def main():
    ipqs = AsyncIPQSConnector(
        api_key=env_config["IPQS_API_KEY"],
        enable_logging=True,
        load_env_vars=True,
        trust_env=True,
        verify=False
    )

    res = await ipqs.malicious_url(
        query="bad.url"
    )

    print(res)
    print(res.json())
    print(res.headers)

asyncio.run(main())
# main()