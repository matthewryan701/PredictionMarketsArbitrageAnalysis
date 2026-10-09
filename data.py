import json
import requests 

# Downloading Polymarket data
POLYMARKET_URL = 'https://gamma-api.polymarket.com'

def fetch_polymarket(limit=100, max_pages=10):
    markets = []
    for page in range(max_pages):
        params = {
            'active': 'true', 
            'closed': 'false', 
            'limit': limit,
            'offset': page * limit,
            'order': 'volume24hr',
            'ascending': 'false'
            }
        response = requests.get(f'{POLYMARKET_URL}/markets', params=params, timeout=10)
        response.raise_for_status()
        batch = response.json()
        markets.extend(batch)
        if len(batch) < limit:
            break
    return markets

# Downloading Kalshi data
KALSHI_URL = 'https://api.elections.kalshi.com/trade-api/v2'

def fetch_kalshi(series_ticker=None, max_pages=5):
    markets = []
    cursor = None
    for _ in range(max_pages):
        params = {'status': 'open', 'limit': 1000, 'mve_filter': 'exclude'}
        if series_ticker:
            params['series_ticker'] = series_ticker
        if cursor:
            params['cursor'] = cursor
        response = requests.get(f'{KALSHI_URL}/markets', params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        markets.extend(data['markets'])
        cursor = data.get('cursor')
        if not cursor:
            break
    return markets

# Downloading Manifold data
MANIFOLD_URL = 'https://api.manifold.markets/v0'

def fetch_manifold(limit=1000):
    params = {'filter': 'open', 'contractType': 'BINARY', 'sort': 'liquidity', 'limit': limit}
    response = requests.get(f'{MANIFOLD_URL}/search-markets', params=params, timeout=10)
    response.raise_for_status()
    return response.json()