from typing import Dict, Any, List
from requests import Response
from .broker import make_request
from .helpers import check_required_env_vars, combine_env_configs

env_config: Dict[str, Any] = combine_env_configs()

def urlscan_search(query: str, **kwargs: Dict[str, Any]) -> Response:
    """Find archived scans of URLs on urlscan.io

    Args:
        query (str): The query term (ElasticSearch Query String Query). Default: "*"

    Returns:
        Response: requests.Response json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'URLSCAN_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://urlscan.io/api/v1/search/'
    headers: Dict = {
        'accept': 'application/json',
        'API-Key': env_config['URLSCAN_API_KEY']
    }
    params: Dict = {
        'q': query,
        **kwargs
    }

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result