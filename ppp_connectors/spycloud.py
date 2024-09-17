from typing import Dict, Any, List
from requests import Response
from .broker import make_request
from .helpers import check_required_env_vars, combine_env_configs


env_config: Dict[str, Any] = combine_env_configs()


def spycloud_sip_cookie_domains(cookie_domains: str, **kwargs: Dict[str, Any]) -> Response:
    """Return botnet sourced cookie data for your domain and its subdomains

    Args:
        cookie_domains (str): This parameter allows you to define a cookie \
            domain to search against, results will include all subdomains. \
            Optionally, a specific cookie subdomain could be used which will \
            result in only that specific cookie subdomain returned.

    Returns:
        Response: requests.Response json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_SIP_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.spycloud.io/sip-v1/breach/data/cookie-domains/{cookie_domains}'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_SIP_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result

def spycloud_ato_email(email_addresses:str, **kwargs: Dict[str, Any]) -> Response:
    """Return account takeover (ATO) breach data related to a comma-separated string of emails

    Args:
        email_addresses (str): a comma-separated list of email addresses (limit of 10 at a time)

    Returns:
        Response: requests.Respone json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_ATO_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.spycloud.io/sp-v2/breach/data/emails/{email_addresses}'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_ATO_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result

def spycloud_ato_ip(ip_address:str, **kwargs: Dict[str, Any]) -> Response:
    """Return account takeover (ATO) breach data related to an IP address

    Args:
        ip_address (str): IP address or network CIDR notation to search \
            for. For CIDR notation, use an underscore instead of a slash.

    Returns:
        Response: requests.Respone json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_ATO_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.spycloud.io/sp-v2/breach/data/ips/{ip_address}'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_ATO_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result

def spycloud_ato_username(username:str, **kwargs: Dict[str, Any]) -> Response:
    """Return account takeover (ATO) breach data related to a username

    Args:
        username (str): Username you wish to search for. You can also \
            search for the sha1, sha256, or sha512 hash of the username.

    Returns:
        Response: requests.Respone json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_ATO_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.spycloud.io/sp-v2/breach/data/usernames/{username}'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_ATO_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result

def spycloud_ato_phone_number(phone_number:str, **kwargs: Dict[str, Any]) -> Response:
    """Return account takeover (ATO) breach data related to a phone number

    Args:
        username (str): phone number you wish to search for. Must only be \
            numerical values of length 7 to 15 characters. You can also \
            search for the sha1, sha256, or sha512 hash of the phone number.

    Returns:
        Response: requests.Respone json response from the request
    """

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_ATO_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.spycloud.io/sp-v2/breach/data/phone-numbers/{phone_number}'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_ATO_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result

def spycloud_ato_breach_catalog(query:str, **kwargs: Dict[str, Any]) -> Response:

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_ATO_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.spycloud.io/sp-v2/breach/catalog'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_ATO_KEY']
    }
    params: Dict = {
        'query': query,
        **kwargs
    }

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result