import requests
from config import *

def check_rug_status(address):
    try:
        response = requests.get(RUGCHECK_API, headers={'accept': 'application/json'})
        if response.status_code == 200:
            tokens = response.json().get('data', [])
            for token in tokens:
                if token.get('address') == address:
                    return token.get('freezeAuthority'), token.get('mintAuthority')
        return None, None
    except Exception as e:
        print(f"RugCheck error: {e}")
        return None, None
