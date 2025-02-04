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
    for index, pool in enumerate(pools):
        try:
            # Vérification de la structure de base
            if not isinstance(pool, dict):
                print(f"Pool {index} n'est pas un dictionnaire valide")
                continue

            # Extraction sécurisée de l'URL
            url = pool.get('url')
            if not url:
                print(f"Pool {index} n'a pas d'URL")
                continue

            # Extraction du pairAddress depuis l'URL
            try:
                pair_address = url.split('/')[-1]
            except AttributeError:
                print(f"Format d'URL invalide pour le pool {index}")
                continue

            # Filtrage par chaîne Solana
            if pool.get('chainId') != 'solana':
                print(f"Pool {index} n'est pas sur Solana")
                continue

            # Requête des détails du pool
            details_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
            details_response = requests.get(details_url)
            
            if details_response.status_code != 200:
                print(f"Échec de récupération des détails pour le pool {index}")
                continue

            pair_data = details_response.json().get('pair', {})
            
            # Conversion sécurisée des valeurs numériques
            try:
                market_cap = float(pair_data.get('marketCap', 0)) or 0
                liquidity = float(pair_data.get('liquidity', {}).get('usd', 0)) or 0
                volume = float(pair_data.get('volume', {}).get('h24', 0)) or 0
            except (TypeError, ValueError) as e:
                print(f"Erreur de conversion pour le pool {index}: {str(e)}")
                continue

            # Extraction des liens avec valeurs par défaut
            links = pool.get('links', [])
            websites = [
                link.get('url') 
                for link in links 
                if isinstance(link, dict) and link.get('label') == 'Website'
            ] or ['']
            
            socials = [
                link.get('url') 
                for link in links 
                if isinstance(link, dict) and link.get('type') in ['twitter', 'telegram']
            ] or ['']

            # Vérification finale des conditions
            if all([
                market_cap >= MIN_MARKET_CAP,
                liquidity >= MIN_LIQUIDITY,
                volume >= MIN_VOLUME,
                any(websites),
                any(socials)
            ]):
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
            print(f"Erreur critique avec le pool {index}: {str(e)}")
            continue

    return valid_pools
                
