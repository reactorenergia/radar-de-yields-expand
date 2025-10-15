import os
import sys
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()

    api_key = os.getenv("EXPAND_KEY")
    if not api_key:
        sys.exit("Error en EXPAND_KEY en .env")

    base_url = os.getenv("EXPAND_BASE_URL", "https://api.expand.network")
    endpoint = f"{base_url}/yieldaggregator/getvaults"

    #Yearn en ETH (ID 5000) + WETH
    params = {
        "yieldAggregatorId": "5000",  # Yearn / Ethereum
        "tokenAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH en ETH
    }
    headers = {"x-api-key": api_key}

    try:
        resp = requests.get(endpoint, params=params, headers=headers, timeout=30)
        print("URL:", resp.url)  # console si sí
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        sys.exit(f"Error HTTP/JSON: {e}")

    if data.get("status") != 200:
        sys.exit(f"Respuesta no OK: {data}")

    token_vaults = data.get("data", {}).get("tokenVaults", [])

    # Normaliza por si viene como dict agrupado por token
    if isinstance(token_vaults, dict):
        flat = []
        for v in token_vaults.values():
            if isinstance(v, list):
                flat.extend(v)
            elif isinstance(v, dict):
                flat.append(v)
        token_vaults = flat

    print("Vaults recibidos:", len(token_vaults))
    for v in token_vaults[:5]:
        apr = (v.get("apr") or {})
        net = apr.get("netAPR")
        print("-", v.get("vaultName"), "|", v.get("vaultSymbol"), "| netAPR:", net)

if __name__ == "__main__":
    main()
