import requests
from config import *

def get_dex_data():
    try:
        response = requests.get(DEXSCREENER_API)
        if response.status_code == 200:
            return response.json()  # La réponse est déjà une liste
        return []
    except Exception as e:
        print(f"Dexscreener API error: {str(e)}")
        return []

def filter_valid_pools(pools):
    valid_pools = []
    for pool in pools:
        try:
            # Vérification de la structure des données
            if not isinstance(pool, dict):
                continue

            # Extraction sécurisée des valeurs
            pair_address = pool.get('url').split('/')[-1]  # Extraction depuis l'URL
            chain_id = pool.get('chainId')
            
            # Requête pour les détails du pool
            details_response = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}")
            if details_response.status_code != 200:
                continue
                
            pair_data = details_response.json().get('pair', {})
            
            # Conversion sécurisée des valeurs numériques
            market_cap = float(pair_data.get('marketCap', 0))
            liquidity = float(pair_data.get('liquidity', {}).get('usd', 0))
            volume = float(pair_data.get('volume', {}).get('h24', 0))
            
            # Vérification des conditions
            if (market_cap >= MIN_MARKET_CAP and
                liquidity >= MIN_LIQUIDITY and
                volume >= MIN_VOLUME and
                pool.get('links') and 
                any(link.get('url') for link in pool.get('links', []))):
                
                valid_pools.append({
                    'address': pool.get('tokenAddress'),
                    'data': {
                        'marketCap': market_cap,
                        'liquidity': {'usd': liquidity},
                        'volume': {'h24': volume},
                        'url': pool.get('url'),
                        'websites': [link['url'] for link in pool.get('links', []) if link.get('label') == 'Website'],
                        'socials': [link['url'] for link in pool.get('links', []) if link.get('type') in ['twitter', 'telegram']]
                    }
                })
                
        except Exception as e:
            print(f"Error processing pool: {str(e)}")
            continue
            
    return valid_pools
