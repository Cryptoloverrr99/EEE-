import requests
from config import *

def check_rug_status(address):
    try:
        response = requests.get(f"https://api.rugcheck.xyz/v1/api/token/{address}")
        if response.status_code == 200:
            data = response.json()
            return data.get('freezeAuthority'), data.get('mintAuthority')
        return None, None
    except Exception as e:
        print(f"RugCheck error: {str(e)}")
        return None, None
