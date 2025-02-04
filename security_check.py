import requests
from config import *

def check_rug_status(address):
    response = requests.get(RUGCHECK_API, headers={'accept': 'application/json'})
    if response.status_code == 200:
        for token in response.json()['data']:
            if token['address'] == address:
                return token['freezeAuthority'], token['mintAuthority']
    return None, None
