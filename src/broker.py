import niquests as requests
from typing import Callable, Dict, Any
from dotenv import dotenv_values


env_config: Dict = dotenv_values('../.env')

if not env_config:
    raise FileNotFoundError('The .env file doesn\'t exist or is empty. Did you copy the'
                            '.env.sample file to .env and set your values?')


def make_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    params: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    json: Dict[str, Any] = None
) -> requests.Response:
    """_summary_

    Args:
        method (str): _description_
        url (str): _description_
        headers (Dict[str, str], optional): _description_. Defaults to None.
        params (Dict[str, Any], optional): _description_. Defaults to None.
        data (Dict[str, Any], optional): _description_. Defaults to None.
        json (Dict[str, Any], optional): _description_. Defaults to None.

    Raises:
        FileNotFoundError: _description_

    Returns:
        requests.Response: _description_
    """

    proxies: Dict = {
        'http_proxy': env_config['HTTP_PROXY'],
        'https_proxy': env_config['HTTPS_PROXY']
    }

    verify: str = False if env_config['VERIFY_SSL'].lower() == "false" else True
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
