import os
import time
import requests
import pandas as pd

# ======================================================
# CONFIG
# ======================================================

CACHE_DIR = "data\\history"

os.makedirs(
    CACHE_DIR,
    exist_ok=True
)

# ======================================================
# SYMBOL NORMALIZATION
# ======================================================

def normalize_symbol(symbol):

    symbol = symbol.upper().strip()

    replacements = {
        "ADA.S": "ADA",
        "ATOM21.S": "ATOM",
        "FLOW14.S": "FLOW",
        "KAVA21.S": "KAVA",
        "SOL03.S": "SOL",
        "SUI.B": "SUI",
        "TAO.B": "TAO",
        "XBT.B": "BTC",
        "XETH": "ETH",
        "XXLM": "XLM",
        "XXMR": "XMR",
        "XXRP": "XRP"
    }

    return replacements.get(
        symbol,
        symbol
    )

# ======================================================
# COINGECKO MAP
# ======================================================

COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    "ALGO": "algorand",
    "ATOM": "cosmos",
    "AVAX": "avalanche-2",
    "BAND": "band-protocol",
    "CRV": "curve-dao-token",
    "FLOW": "flow",
    "HBAR": "hedera-hashgraph",
    "KAS": "kaspa",
    "KAVA": "kava",
    "LIT": "litentry",
    "MANA": "decentraland",
    "QNT": "quant-network",
    "SOL": "solana",
    "SUI": "sui",
    "TAO": "bittensor",
    "TRX": "tron",
    "USDC": "usd-coin",
    "XAUT": "tether-gold",
    "XDC": "xdc-network",
    "XLM": "stellar",
    "XMR": "monero",
    "XRP": "ripple",
    "ZRO": "layerzero"
}

# ======================================================
# HTTP
# ======================================================

def safe_get(url, params=None):

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code == 429:

            print(
                "\nRATE LIMITED\n"
                "Stop and retry later."
            )

            return None

        if response.status_code != 200:

            print(
                f"HTTP {response.status_code}"
            )

            return None

        return response.json()

    except Exception as e:

        print(
            "Request Error:",
            e
        )

        return None

# ======================================================
# CACHE
# ======================================================

def history_file(coin_id):

    return os.path.join(
        CACHE_DIR,
        f"{coin_id}.csv"
    )

# ======================================================
# DOWNLOAD
# ======================================================

def download_history(coin_id):

    filename = history_file(
        coin_id
    )

    if os.path.exists(filename):

        print(
            f"SKIP - Cached: {coin_id}"
        )

        return True

    print(
        f"DOWNLOAD: {coin_id}"
    )

    url = (
        f"https://api.coingecko.com/api/v3/coins/"
        f"{coin_id}/market_chart"
    )

    data = safe_get(
        url,
        {
            "vs_currency": "usd",
            "days": 365
        }
    )

    if not data:
        return False

    prices = data.get(
        "prices",
        []
    )

    if len(prices) == 0:

        print(
            f"No Data: {coin_id}"
        )

        return False

    df = pd.DataFrame(
        prices,
        columns=[
            "timestamp",
            "price"
        ]
    )

    df.to_csv(
        filename,
        index=False
    )

    print(
        f"Saved: {filename}"
    )

    return True

# ======================================================
# MAIN
# ======================================================

def main():

    if not os.path.exists(
        "kraken_balances_20260704_135003.csv"
    ):

        print(
            "Missing Kraken balances file"
        )

        return

    holdings = pd.read_csv(
        "kraken_balances_20260704_135003.csv"
    )

    downloaded = 0
    skipped = 0
    unmapped = 0

    for _, row in holdings.iterrows():

        original = str(
            row["Asset"]
        ).upper()

        symbol = normalize_symbol(
            original
        )

        coin_id = COINGECKO_MAP.get(
            symbol
        )

        if coin_id is None:

            print(
                f"UNMAPPED: {original}"
            )

            unmapped += 1
            continue

        filepath = history_file(
            coin_id
        )

        if os.path.exists(filepath):

            skipped += 1

            print(
                f"CACHED: {coin_id}"
            )

            continue

        success = download_history(
            coin_id
        )

        if success:
            downloaded += 1

        # intentionally slow
        time.sleep(20)

    print("\n")
    print("=" * 60)
    print("HISTORICAL DATA COLLECTION COMPLETE")
    print("=" * 60)

    print(
        f"Downloaded : {downloaded}"
    )

    print(
        f"Cached     : {skipped}"
    )

    print(
        f"Unmapped   : {unmapped}"
    )

    print(
        f"Directory  : {CACHE_DIR}"
    )

if __name__ == "__main__":
    main()