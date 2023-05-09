from urllib.parse import parse_qs, urlencode, urlsplit
from typing import Any, Dict
import requests
from datetime import datetime

missing_ids = ['catalog', 'status']
user_agent = 'vinted-ios Vinted/22.6.1 (lt.manodrabuziai.fr; build:21794; iOS 15.2.0) iPhone10,6'
device_model = 'iPhone10,6'
app_version = '22.6.1'

session = {}


def get_oauth_token() -> Dict[str, str]:
    global session

    payload = {
        "grant_type": "password",
        "client_id": "ios",
        "scope": "public"
    }

    if (session and 'refresh_token' in session):
        payload['grant_type'] = 'refresh_token'
        payload['refresh_token'] = session['refresh_token']
    
    response = requests.post(
        url='https://www.vinted.fr/oauth/token',
        headers={
            'User-Agent': user_agent,
        },
        json=payload,
    )

    if response.status_code != 200:
        raise Exception('Failed to get oauth token')

    content = response.json()

    return {
        'access_token': content['access_token'],
        'refresh_token': content['refresh_token'],
        'expiration_date': content['created_at'] + content['expires_in']
    }


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


def search(url: str, query: Dict[str, str] = {}) -> Dict[str, Any]:
    """
    Search items from the Vinted API
    using a web URL.


    Args:
        url (str): Original URL
        query (Dict[str, str]): Additional queries to merge

    Returns:
        Any: JSON results
    """

    global session

    if (not session or session['expiration_date'] < datetime.now().timestamp()):
        session = get_oauth_token()

    query = dict(parse_url(url), **query)

    response = requests.get(
        url='https://www.vinted.fr/api/v2/catalog/items?' + urlencode(query),
        headers={
            'Authorization': f'Bearer {session["access_token"]}',
            'User-Agent': user_agent,
            'x-app-version': app_version,
            'x-device-model': device_model,
            'short-bundle-version': app_version,
            'Accept': 'application/json'
        }
    )
    
    if response.status_code != 200:
        raise Exception('Failed to search')

    return response.json()
