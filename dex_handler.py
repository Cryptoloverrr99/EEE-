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

# dex_handler.py
def filter_valid_pools(pools):
    valid_pools = []
    for index, pool in enumerate(pools):
        try:
            # Debug: Afficher la structure complète du pool
            print(f"Processing pool {index + 1}/{len(pools)}:", pool)
            
            # Vérification de base de la structure
            if not isinstance(pool, dict):
                print(f"Pool {index} is not a dictionary")
                continue
                
            # Extraction sécurisée des URLs
            url = pool.get('url')
            if not url:
                print(f"Pool {index} missing URL")
                continue
                
            # Extraction du pairAddress depuis l'URL
            pair_address = url.split('/')[-1]
            if not pair_address:
                print(f"Invalid URL format for pool {index}")
                continue
                
            # Vérification de la chaîne
            chain_id = pool.get('chainId')
            if chain_id != 'solana':  # Filtre uniquement Solana
                print(f"Pool {index} is not on Solana")
                continue
                
            # Récupération des détails du pool
            details_url = f"https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}"
            details_response = requests.get(details_url)
            
            if details_response.status_code != 200:
                print(f"Failed to fetch details for pool {index}")
                continue
                
            pair_data = details_response.json().get('pair', {})
            
            # Conversion sécurisée des valeurs
            try:
                market_cap = float(pair_data.get('marketCap', 0))
                liquidity = float(pair_data.get('liquidity', {}).get('usd', 0))
                volume = float(pair_data.get('volume', {}).get('h24', 0))
            except (TypeError, ValueError) as e:
                print(f"Conversion error in pool {index}: {str(e)}")
                continue
                
            # Extraction des liens
            links = pool.get('links', [])
            websites = [link.get('url') for link in links if link.get('label') == 'Website']
            socials = [link.get('url') for link in links if link.get('type') in ['twitter', 'telegram']]
            
            # Vérification finale des conditions
            if (market_cap >= MIN_MARKET_CAP and
                liquidity >= MIN_LIQUIDITY and
                volume >= MIN_VOLUME and
                len(websites) > 0 and
                len(socials) > 0):
                
                valid_pools.append({
                    'address': pool.get('tokenAddress'),
                    'data': {
                        'marketCap': market_cap,
                        'liquidity': {'usd': liquidity},
                        'volume': {'h24': volume},
                        'url': url,
                        'websites': websites,
                        'socials': socials
                    }
                })
                
        except Exception as e:
            print(f"Critical error processing pool {index}: {str(e)}")
            continue
            
    return valid_pools
