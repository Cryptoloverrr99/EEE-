import time
import logging
from dex_handler import *
from security_check import *
from solana_analyzer import *
from alert_bot import *

logging.basicConfig(level=logging.INFO)
processed_addresses = set()

def format_alert(data):
    return f"""
🚨 <b>New Safe Memecoin Detected</b> 🚨

📌 <b>Basic Info</b>
- Market Cap: ${data.get('marketCap', 0):,.2f}
- Liquidity: ${data.get('liquidity', {}).get('usd', 0):,.2f}
- 24h Volume: ${data.get('volume', {}).get('h24', 0):,.2f}

🔗 <b>Links</b>
- Website: {data.get('websites', [''])[0]}
- Socials: {', '.join(data.get('socials', []))}

🔒 <b>Security Status</b>
- Freeze Authority: Revoked ❌
- Mint Authority: Revoked ❌

📊 <a href="{data.get('url', '#')}">DexScreener Chart</a>
"""

def main_loop():
    while True:
        try:
            logging.info("Starting new scan cycle...")
            
            # Étape 1: Récupération des données Dexscreener
            new_pools = get_dex_data()
            logging.info(f"Found {len(new_pools)} raw pools")
            
            # Étape 2: Filtrage des pools valides
            valid_pools = filter_valid_pools(new_pools)
            logging.info(f"Valid pools after filtering: {len(valid_pools)}")
            
            # Étape 3: Traitement des nouvelles adresses
            for pool in valid_pools:
                address = pool.get('address')
                if address and address not in processed_addresses:
                    logging.info(f"New address detected: {address}")
                    
                    # Étape 4: Vérification RugCheck
                    freeze, mint = check_rug_status(address)
                    if freeze == 'revoked' and mint == 'revoked':
                        # Étape 5: Récupération métadonnées Solscan
                        sol_data = get_solscan_meta(address)
                        if sol_data:
                            # Étape 6: Envoi de l'alerte
                            alert_message = format_alert(pool['data'])
                            send_telegram_alert(alert_message)
                            processed_addresses.add(address)
                            logging.info("Alert sent successfully!")
            
            # Temporisation principale
            logging.info("Cycle completed, sleeping...")
            time.sleep(180)
            
        except Exception as e:
            logging.error(f"Critical error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main_loop()
