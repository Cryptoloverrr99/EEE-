import requests
from config import *

def get_dex_data():
    response = requests.get(DEXSCREENER_API)
    if response.status_code != 200:
        return []
    
    # Debug: Afficher la structure de la réponse
    print("Dexscreener raw response:", response.json())
    
    # Nouvelle structure de réponse
    return response.json().get('results', [])  # Adapté à la vraie structure
    
def filter_valid_pools(pools):
    valid_pools = []
    for pool in pools:
        # Vérification de la structure des données
        if not isinstance(pool, dict):
            continue
            
        # Extraction sécurisée des valeurs
        pair_address = pool.get('pairAddress')
        chain_id = pool.get('chainId')
        
        if not pair_address or not chain_id:
            continue
            
        # Requête pour les détails
        details_response = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}")
        if details_response.status_code != 200:
            continue
            
        details = details_response.json()
        pair_data = details.get('pair', {})
        
        # Vérification des types de données
        try:
            market_cap = float(pair_data.get('marketCap', 0))
            liquidity = float(pair_data.get('liquidity', {}).get('usd', 0))
            volume = float(pair_data.get('volume', {}).get('h24', 0))
        except (TypeError, ValueError):
            continue
            
        # Vérification des conditions
        if (market_cap >= MIN_MARKET_CAP and
            liquidity >= MIN_LIQUIDITY and
            volume >= MIN_VOLUME and
            pair_data.get('websites') and 
            pair_data.get('socials')):
            
            valid_pools.append({
                'address': pair_data.get('baseToken', {}).get('address'),
                'data': pair_data
            })
    
    return valid_pools
