from typing import Dict, Any, List
from requests import Response
from .broker import make_request
from .helpers import check_required_env_vars, combine_env_configs

env_config: Dict[str, Any] = combine_env_configs()

def urlscan_search(query: str, **kwargs: Dict[str, Any]) -> Response:
    """Find archived scans of URLs on urlscan.io. Search query syntax can
        be found at https://urlscan.io/docs/search/

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

def urlscan_scan(query: str, **kwargs: Dict[str, Any]) -> Response:
    """Submit a URL to be scanned

    Args:
        query (str): the URL to be scanned

    Returns:
        Response: requests.Response json response from the request
    """

    required_vars: List[str] = [
        'URLSCAN_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'post'
    url: str = 'https://urlscan.io/api/v1/scan'
    headers: Dict = {
        'accept': 'application/json',
        'API-Key': env_config['URLSCAN_API_KEY']
    }
    payload: Dict = {
        'url': query,
        **kwargs
    }

    result: Response = make_request(method=method, url=url, headers=headers, json=payload)

    return result

def urlscan_results(uuid: str, **kwargs: Dict[str, Any]) -> Response:
    """Retrieve results of a URLScan scan

    Args:
        uuid (str): the UUID of the submitted URL scan

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
    url: str = f'https://urlscan.io/api/v1/result/{uuid}'
    headers: Dict = {
        'accept': 'application/json',
        'API-Key': env_config['URLSCAN_API_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result