from typing import Dict, Any, List
from requests import Response
from .broker import make_request
from .helpers import check_required_env_vars, combine_env_configs


env_config: Dict[str, Any] = combine_env_configs()

def flashpoint_search_communities(query: str, **kwargs: Dict[str, Any]) -> Response:
    """Communities Search allows search requests over article and conversation data.
    Article data is made up of things like blogs and paste sites. Conversation data
    is made up of chats, forums, and social media posts.

    Args:
        query (str): A word or phrase to search.

    Returns:
        Response: requests.Response object from the request
    """

    required_vars: List[str] = [
        'FLASHPOINT_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'post'
    url: str = 'https://api.flashpoint.io/sources/v2/communities'
    headers: Dict = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {env_config["FLASHPOINT_API_KEY"]}'
    }
    payload: Dict = {
        'query': query,
        **kwargs
    }

    result: Response = make_request(method=method, url=url, headers=headers, json=payload)

    return result

def flashpoint_search_media(query: str, **kwargs: Dict[str, Any]) -> Response:
    """Media search allows search requests over our media data, specifically
    media that have been through our Optical Character Recogintion (OCR) process.
    Once media have been through our OCR process, any text, classifications, or
    logos found within the media are available for search.

    Args:
        query (str): A word or phrase to search.

    Returns:
        Response: requests.Response object from the request
    """

    required_vars: List[str] = [
        'FLASHPOINT_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'post'
    url: str = 'https://api.flashpoint.io/sources/v2/media'
    headers: Dict = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {env_config["FLASHPOINT_API_KEY"]}'
    }
    payload: Dict = {
        'query': query,
        **kwargs
    }

    result: Response = make_request(method=method, url=url, headers=headers, json=payload)

    return result

def flashpoint_get_media_object(id: str) -> Response:
    """Media ID request allows users to directly lookup the document based on the media ID provided.

    Args:
        id (str): the id of the media object to retrieve

    Returns:
        Response: requests.Response object from the request
    """

    required_vars: List[str] = [
        'FLASHPOINT_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.flashpoint.io/sources/v2/media/{id}'
    headers: Dict = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {env_config["FLASHPOINT_API_KEY"]}'
    }

    result: Response = make_request(method=method, url=url, headers=headers)

    return result

def flashpoint_get_media_image(storage_uri: str) -> Response:
    """Download the media from a media object by its storage_uri field

    Args:
        storage_uri (str): the storage_uri field from the media object

    Returns:
        Response: requests.Response object from the request
    """

    required_vars: List[str] = [
        'FLASHPOINT_API_KEY'
    ]

    # Check and ensure that required variables are present, exits if not
    check_required_env_vars(env_config, required_vars)

    method: str = 'get'
    url: str = f'https://api.flashpoint.io/sources/v1/media/'
    headers: Dict = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': f'Bearer {env_config["FLASHPOINT_API_KEY"]}'
    }

    params = {
        "asset_id": storage_uri
    }

    result: Response = make_request(method=method, url=url, headers=headers, params=params)

    return result