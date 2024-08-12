import sys
from typing import Callable, Dict, Any, List
import requests
from .helpers import check_required_env_vars, combine_env_configs


env_config: Dict[str, Any] = combine_env_configs()


def make_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    params: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    json: Dict[str, Any] = None
) -> requests.Response:
    """Perform an HTTP request on behalf of a calling function

    Args:
        method (str): the HTTP method to use
        url (str): the API URL to call
        headers (Dict[str, str], optional): the HTTP headers to use in the request. Defaults to None.
        params (Dict[str, Any], optional): the query parameters to use in the request. Defaults to None.
        data (Dict[str, Any], optional): the data to use in the request. Defaults to None.
        json (Dict[str, Any], optional): the json data to use in the request. Defaults to None.

    Raises:
        ValueError: this will raise if an invalid HTTP method is passed

    Returns:
        requests.Response: the HTTP response from the request
    """

    # Define required environment variables
    required_vars: List[str] = []

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    proxies: Dict[str, Any] = {
        'http': env_config['HTTP_PROXY'] if 'HTTP_PROXY' in env_config else '',
        'https': env_config['HTTPS_PROXY'] if 'HTTPS_PROXY' in env_config else ''
    }

    verify: bool = False if 'VERIFY_SSL' in env_config and env_config['VERIFY_SSL'].lower() == 'false' else True
    if verify is False:
        import urllib3
        urllib3.disable_warnings()

    method_map: Dict[str, Callable] = {
        'GET': requests.get,
        'POST': requests.post,
        'PUT': requests.put,
        'DELETE': requests.delete,
        'PATCH': requests.patch
    }

    request_func = method_map.get(method.upper())
    if not request_func:
        raise ValueError(f'Unsupported HTTP method: {method}')

    return request_func(url, headers=headers, params=params, data=data, json=json, proxies=proxies, verify=verify)
