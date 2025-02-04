import requests
from config import *

def get_dex_data():
    response = requests.get(DEXSCREENER_API)
    return response.json()['data'] if response.status_code == 200 else []

def filter_valid_pools(pools):
    valid_pools = []
    for pool in pools:
        details = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/{pool['chainId']}/{pool['pairId']}").json()
        pair_data = details['pair']
        
        if (pair_data['marketCap'] >= MIN_MARKET_CAP and
            pair_data['liquidity']['usd'] >= MIN_LIQUIDITY and
            pair_data['volume']['h24'] >= MIN_VOLUME and
            pair_data['websites'] and
            pair_data['socials']):
            
            valid_pools.append({
                'address': pool['quoteToken']['address'],
                'data': pair_data
            })
    return valid_pools
