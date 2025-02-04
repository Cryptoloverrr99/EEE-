from tenacity import retry, stop_after_attempt, wait_fixed
import requests
from config import *

# Déplacer la fonction extract_pair_address ICI
def extract_pair_address(url):
    parts = url.rstrip('/').split('/')
    return parts[-1] if len(parts) > 1 else None

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_dex_data():
    try:
        response = requests.get(DEXSCREENER_API)
        response.raise_for_status()
        data = response.json()
        
        # Debug: Afficher les premières entrées
        print("Raw API response sample:", data.get('pairs', [])[:1])
        
        return data.get('pairs', [])  # Clé correcte pour les pools
    except Exception as e:
        print(f"Erreur API détaillée: {str(e)}")
        return []

def filter_valid_pools(pools):
    valid_pools = []
    for pool in pools:
        try:
            # Vérification des clés obligatoires
            required_keys = {
                'baseToken': ['address'],
                'liquidity': ['usd'],
                'volume': ['h24'],
                'url': None
            }
            
            for key, subkeys in required_keys.items():
                if key not in pool:
                    raise KeyError(f"{key} manquant")
                if subkeys:
                    for subkey in subkeys:
                        if subkey not in pool[key]:
                            raise KeyError(f"{key}.{subkey} manquant")
            
            # Extraction des valeurs
            market_cap = float(pool.get('marketCap', 0))
            liquidity = float(pool['liquidity']['usd'])
            volume = float(pool['volume']['h24'])
            url = pool['url']
            token_address = pool['baseToken']['address']
            
            # Vérification des seuils
            if (market_cap >= MIN_MARKET_CAP and
                liquidity >= MIN_LIQUIDITY and
                volume >= MIN_VOLUME):
                
                valid_pools.append({
                    'address': token_address,
                    'data': {
                        'marketCap': market_cap,
                        'liquidity': {'usd': liquidity},
                        'volume': {'h24': volume},
                        'url': url,
                        'websites': [link['url'] for link in pool.get('links', []) if link.get('label') == 'Website'],
                        'socials': [link['url'] for link in pool.get('links', []) if link.get('type') in ['twitter', 'telegram']]
                    }
                })
                
        except Exception as e:
            print(f"Pool invalide: {str(e)}")
            continue
            
    return valid_pools
