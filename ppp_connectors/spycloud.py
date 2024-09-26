from typing import Dict, Any, List
from requests import Response
import sys
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
        Response: requests.Response json response from the request
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
    """List or Query the Breach Catalog


    Args:
        query (str): Query value to search the breach catalog for.


    Returns:
        Response: requests.Response json response from the request
    """

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

def spycloud_inv_search(search_type: str, query:str, **kwargs: Dict[str, Any]) -> Response:

    # Define required environment variables
    required_vars: List[str] = [
        'SPYCLOUD_API_INV_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    # These are valid endpoints and their corresponding full URLs. We'll use these
    # to check that the user passed a valid 'search_type' parameter
    base_url: str = 'https://api.spycloud.io/investigations-v2/breach/data'
    valid_endpoints: Dict[str, str] = {
        'domain': f'{base_url}/domains',
        'email': f'{base_url}/emails',
        'ip': f'{base_url}/ips',
        'infected-machine-id': f'{base_url}/infected-machine-ids',
        'log-id': f'{base_url}/log-ids',
        'password': f'{base_url}/passwords',
        'username': f'{base_url}/usernames',
        'email-username': f'{base_url}/email-usernames',
        'phone-number': f'{base_url}/phone-numbers',
        'social-handle': f'{base_url}/social-handles',
        'bank-number': f'{base_url}/bank-numbers',
        'cc-number': f'{base_url}/cc-numbers',
        'drivers-license': f'{base_url}/drivers-licenses',
        'national-id': f'{base_url}/national-ids',
        'passport-number': f'{base_url}/passport-numbers',
        'ssn': f'{base_url}/social-security-numbers',
    }

    # Completely exit if they supply an invalid search_type
    if search_type not in valid_endpoints:
        print(f'[!] Error: {search_type} is not a valid search type. Must be one of '
              f'{", ".join(valid_endpoints.keys())}', file=sys.stderr)
        sys.exit(1)

    method: str = 'get'
    url: str = f'{valid_endpoints[search_type]}/{query}'

    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_INV_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result

