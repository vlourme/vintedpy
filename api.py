from urllib.parse import parse_qs, urlencode, urlsplit
from typing import Any, Dict
import requests
from tenacity import retry

missing_ids = ['catalog', 'status']
user_agent = 'vinted-ios Vinted/22.6.1 (lt.manodrabuziai.fr; build:21794; iOS 15.2.0) iPhone10,6'
device_model = 'iPhone10,6'
app_version = '22.6.1'


@retry
def get_cookie() -> str:
    """
    Get a session cookie

    Raises:
        Exception: Exception if cookie does not exists

    Returns:
        str: cookie
    """
    response = requests.get(
        url='https://vinted.fr',
        headers={
            'User-Agent': user_agent,
            'x-app-version': app_version,
            'x-device-model': device_model,
            'short-bundle-version': app_version
        }
    )
    cookie = response.cookies.get('_vinted_fr_session')

    if not cookie:
        raise Exception('cannot get session cookie')

    return cookie


def parse_url(url: str) -> Dict[str, str]:
    """
    Parse query strings

    Args:
        url (str): Web URL

    Returns:
        Dict[str, str]: Query values as dict
    """
    parts = urlsplit(url)
    query = parse_qs(parts.query)
    results = {}

    for q, v in query.items():
        is_array = False

        if q.endswith('[]'):
            q = q.rstrip('[]')
            is_array = True

        if q in missing_ids:
            q += '_id'

        if not q.endswith('s') and is_array:
            q += 's'

        results[q] = ','.join(v)

    return results


@retry
def search(url: str, query: Dict[str, str] = {}) -> Any:
    """
    Search items from the Vinted API
    using a web URL.


    Args:
        url (str): Original URL
        query (Dict[str, str]): Additional queries to merge

    Returns:
        Any: JSON results
    """

    session = get_cookie()
    query = dict(parse_url(url), **query)

    response = requests.get(
        url='https://www.vinted.fr/api/v2/catalog/items?' + urlencode(query),
        headers={
            'Cookie': '_vinted_fr_session=' + session,
            'User-Agent': user_agent,
            'x-app-version': app_version,
            'x-device-model': device_model,
            'short-bundle-version': app_version,
            'Accept': 'application/json'
        }
    )

    return response.json()
