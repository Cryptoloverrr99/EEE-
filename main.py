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
        print(f"Found {len(new_pools)} pools from Dexscreener")
        
        valid_pools = filter_valid_pools(new_pools)
        print(f"Valid pools after filtering: {len(valid_pools)}")
        
        for pool in valid_pools:
            print(f"Processing pool: {pool['address']}")
            # ... reste du code ...
