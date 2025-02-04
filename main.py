import time
from dex_handler import *
from security_check import *
from solana_analyzer import *
from alert_bot import *

processed_addresses = set()

def format_alert(data):
    return f"""
🚨 <b>New Safe Memecoin Detected</b> 🚨
    
📌 <b>Basic Info</b>
- Market Cap: ${data['marketCap']:,.2f}
- Liquidity: ${data['liquidity']['usd']:,.2f}
- 24h Volume: ${data['volume']['h24']:,.2f}
    
🔗 <b>Links</b>
- Website: {data['websites'][0]}
- Socials: {', '.join(data['socials'])}
    
🔒 <b>Security Status</b>
- Freeze Authority: Revoked ❌
- Mint Authority: Revoked ❌
    
📊 <a href="{data['url']}">DexScreener Chart</a>
"""

while True:
    try:
        new_pools = get_dex_data()
        valid_pools = filter_valid_pools(new_pools)
        
        for pool in valid_pools:
            address = pool['address']
            if address not in processed_addresses:
                freeze, mint = check_rug_status(address)
                
                if freeze == 'revoked' and mint == 'revoked':
                    sol_data = get_solscan_meta(address)
                    alert_message = format_alert(pool['data'])
                    send_telegram_alert(alert_message)
                    processed_addresses.add(address)
        
        time.sleep(180)  # 3 minutes
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
