import sys
from typing import Callable, Dict, Any, List
from dotenv import dotenv_values, find_dotenv
import niquests
from .helpers import check_required_env_vars


env_config: Dict = dotenv_values(find_dotenv())

if not env_config:
    print('[!] Error: The .env file doesn\'t exist or is empty. Did you copy the'
          '.env.sample file to .env and set your values?', file=sys.stderr)
    sys.exit(1)


def make_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    params: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    json: Dict[str, Any] = None
) -> niquests.Response:
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
        niquests.Response: the HTTP response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'HTTP_PROXY',
        'HTTPS_PROXY',
        'VERIFY_SSL'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    proxies: Dict = {
        'http': env_config['HTTP_PROXY'],
        'https': env_config['HTTPS_PROXY']
    }

    verify: str = False if env_config['VERIFY_SSL'].lower() == "false" else True
    if verify is False:
        import urllib3
        urllib3.disable_warnings()

    method_map: Dict[str, Callable] = {
        'GET': niquests.get,
        'POST': niquests.post,
        'PUT': niquests.put,
        'DELETE': niquests.delete,
        'PATCH': niquests.patch
    }

    request_func = method_map.get(method.upper())
    if not request_func:
        raise ValueError(f'Unsupported HTTP method: {method}')

    return request_func(url, headers=headers, params=params, data=data, json=json, proxies=proxies, verify=verify)
