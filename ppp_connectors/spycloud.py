import sys
from typing import Dict, Any
from dotenv import dotenv_values, find_dotenv
from niquests import Response
from .broker import make_request


env_config: Dict = dotenv_values(find_dotenv())

if not env_config:
    print('[!] The .env file doesn\'t exist or is empty. Did you copy the'
          '.env.sample file to .env and set your values?', file=sys.stderr)
    sys.exit(1)

def spycloud_sip_cookie_domains(cookie_domains: str, **kwargs: Dict[str, Any]) -> Response:
    method: str = 'get'
    url: str = f'https://api.spycloud.io/sip-v1/breach/data/cookie-domains/{cookie_domains}'
    headers: Dict = {
        'accept': 'application/json',
        'x-api-key': env_config['SPYCLOUD_API_SIP_KEY']
    }
    params: Dict = dict(kwargs)

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result