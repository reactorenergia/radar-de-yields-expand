#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import os
import sys
import json
import argparse
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

def normalize_token_vaults(tv: Any) -> List[Dict[str, Any]]:
    if isinstance(tv, list):
        return tv
    if isinstance(tv, dict):
        flat: List[Dict[str, Any]] = []
        for v in tv.values():
            if isinstance(v, list):
                flat.extend(v)
            elif isinstance(v, dict):
                inner = v.get("tokenVaults")
                if isinstance(inner, list):
                    flat.extend(inner)
            else:
                flat.append(v)
        return flat
    return []
def to_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        import math
        return float("NaN")

def extract_netapr(v: Dict[str, Any]) -> float:
    apr = v.get("apr") or {}
    return to_float(apr.get("netAPR"))

def main():
    load_dotenv()

    api_key = os.getenv("EXPAND_KEY")
    if not api_key:
        sys.exit("Error en EXPAND_KEY en .env")

    base_url = os.getenv("EXPAND_BASE_URL", "https://api.expand.network")
    endpoint = f"{base_url}/yieldaggregator/getvaults"

    p = argparse.ArgumentParser(description="cli-get vaults + netAPR (ordenado)Yearn/ETH/WETH, --raw para ver JSON")
    p.add_argument("--aggregator", default="yearn", help="yearn infra")
    p.add_argument("--chain", default="ethereum", help="ethereum - por ahora")
    p.add_argument("--token", help="tokenAddress para yearn/harvest")
    p.add_argument("--raw", action="store_true", help="imprimir JSON raw")
    args = p.parse_args()

    if (args.aggregator.strip().lower(), args.chain.strip().lower()) != ("yearn", "ethereum"):
        sys.exit("Script soporta --aggregator yearn --chain ethereum")
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

    if args.raw:
        print(json.dumps(data, indent=2))
        return
    if data.get("status") != 200:
        sys.exit(f"Respuesta NO ok: {data}")
    
    token_vaults = normalize_token_vaults(data.get("data", {}.get("tokenVaults", [])))

    import math
    token_vaults.sort(
        key=lambda v: (extract_netapr(v) if extract_netapr(v) == extract_netapr(v) else -math.inf),
        reverse=True
    )
    print("Vaults recibidos:", len(token_vaults))
    for v in token_vaults[:5]:
        apr = (v.get("apr") or {})
        net = apr.get("netAPR")
        print("-", v.get("vaultName"), "|", v.get("vaultSymbol"), "| netAPR:", net, "|", v.get("vaultAddress"))

if __name__ == "__main__":
    main()
