from tenacity import retry, stop_after_attempt, wait_fixed  # Ligne 1
import requests                                             # Ligne 2
from config import *                                        # Ligne 3

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))      # Ligne 5 (pas d'indentation)
def get_dex_data():                                         # Ligne 6 (alignée avec le décorateur)
    try:
        response = requests.get(DEXSCREENER_API)
        response.raise_for_status()
        return response.json().get('results', [])
    except Exception as e:
        print(f"Erreur API: {str(e)}")
        return []

def filter_valid_pools(pools):
    valid_pools = []
    for index, pool in enumerate(pools):
        try:
            # Vérification fondamentale de l'intégrité des données
            if not pool or not isinstance(pool, dict):
                print(f"Pool {index} invalide ou vide")
                continue

            # Gestion des valeurs None pour les clés critiques
            chain_id = pool.get('chainId') or ''
            url = pool.get('url') or ''
            token_address = pool.get('tokenAddress') or ''

            # Filtrage strict des pools non-Solana
            if chain_id.lower() != 'solana':
                print(f"Pool {index} ignoré (chaîne: {chain_id})")
                continue

            def extract_pair_address(url):
    parts = url.rstrip('/').split('/')
    return parts[-1] if len(parts) > 1 else None

            # Requête des détails avec timeout
            try:
                details_response = requests.get(
                    f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}",
                    timeout=10
                )
                if details_response.status_code != 200:
                    continue
            except requests.exceptions.RequestException as e:
                print(f"Erreur réseau pour le pool {index}: {str(e)}")
                continue

            # Validation de la structure des données
            pair_data = details_response.json().get('pair') or {}
            if not pair_data:
                print(f"Données manquantes pour le pool {index}")
                continue

            # Conversion robuste avec logging
            try:
                market_cap = float(pair_data.get('marketCap') or 0)
                liquidity = float((pair_data.get('liquidity') or {}).get('usd') or 0)
                volume = float((pair_data.get('volume') or {}).get('h24') or 0)
            except (TypeError, ValueError) as e:
                print(f"Erreur de conversion pour le pool {index}: {str(e)}")
                continue

            # Extraction sécurisée des liens
            links = pool.get('links') or []
            websites = []
            socials = []
            
            for link in links:
                if isinstance(link, dict):
                    if link.get('label') == 'Website':
                        websites.append(link.get('url') or '')
                    elif link.get('type') in ['twitter', 'telegram']:
                        socials.append(link.get('url') or '')

            # Validation finale
            if (market_cap >= MIN_MARKET_CAP and
                liquidity >= MIN_LIQUIDITY and
                volume >= MIN_VOLUME and
                len(websites) > 0 and
                len(socials) > 0):
                
                valid_pools.append({
                    'address': token_address,
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
            print(f"Erreur non gérée (pool {index}): {str(e)}")
            continue

    return valid_pools
