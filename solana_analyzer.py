import requests
from config import *

def get_solscan_meta(address):
    response = requests.get(f"{SOLSCAN_API}?address={address}")
    return response.json() if response.status_code == 200 else None
