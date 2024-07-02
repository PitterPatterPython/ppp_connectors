import sys
from typing import Dict, Any, List, Set
from dotenv import dotenv_values, find_dotenv
from niquests import Response
from .broker import make_request

# Load environment variables
env_config: Dict = dotenv_values(find_dotenv())

if not env_config:
    print('[!] Error: The .env file doesn\'t exist or is empty. Did you copy the'
          '.env.sample file to .env and set your values?', file=sys.stderr)
    sys.exit(1)

def check_required_env_vars(config: Dict[str, str], required_vars: List[str]) -> None:
    """Ensure that the env variables required for a function are present in the .env file.

    Args:
        config (Dict[str, str]): the env_config variable that contains values from the .env file
        required_vars (List[str]): the env variables required for a function to successfully function
    """

    missing_vars: Set[str] = set(required_vars) - set(config.keys())
    if missing_vars:
        print(f"[!] Error: missing required environment variables: {', '.join(missing_vars)}. "
              "Please ensure these are present in your .env file.", file=sys.stderr)
        sys.exit(1)

def spycloud_sip_cookie_domains(cookie_domains: str, **kwargs: Dict[str, Any]) -> Response:
    """Return botnet sourced cookie data for your domain and its subdomains

    Args:
        cookie_domains (str): the domain and subdomains to search against

    Returns:
        Response: niquests.Response json response from the request
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