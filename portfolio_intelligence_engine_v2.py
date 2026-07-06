import os
import time
import requests
import pandas as pd
import numpy as np

# ==================================================
# CONFIG
# ==================================================

INPUT_FILE = "kraken_balances_20260704_135003.csv"
OUTPUT_FILE = "portfolio_intelligence_report_v2.csv"

CACHE_DIR = "data\\history"

os.makedirs(CACHE_DIR, exist_ok=True)

# ==================================================
# SYMBOL NORMALIZATION
# ==================================================

def normalize_symbol(symbol):

    symbol = symbol.upper()

    replacements = {
        "XBT": "BTC",
        "XBT.B": "BTC",
        "XETH": "ETH",
        "XXMR": "XMR",
        "XXLM": "XLM",
        "XXRP": "XRP",
        "ADA.S": "ADA",
        "ATOM21.S": "ATOM",
        "FLOW14.S": "FLOW",
        "KAVA21.S": "KAVA",
        "SUI.B": "SUI",
        "TAO.B": "TAO",
        "SOL03.S": "SOL"
    }

    return replacements.get(symbol, symbol)

# ==================================================
# COINGECKO MAP
# ==================================================

COINGECKO_MAP = {
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

BTC_ID = "bitcoin"

# ==================================================
# HTTP
# ==================================================

def safe_get(url, params=None):

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            print(
                f"HTTP {response.status_code}"
            )
            return None

        return response.json()

    except Exception as e:

        print(e)

        return None

# ==================================================
# CACHE
# ==================================================

def cache_file(coin_id):

    return os.path.join(
        CACHE_DIR,
        f"{coin_id}.csv"
    )

# ==================================================
# HISTORY
# ==================================================

def load_history(coin_id):

    filename = cache_file(coin_id)

    if os.path.exists(filename):

        df = pd.read_csv(filename)

        return df

    print(f"Downloading {coin_id}")

    url = (
        f"https://api.coingecko.com/api/v3/"
        f"coins/{coin_id}/market_chart"
    )

    data = safe_get(
        url,
        {
            "vs_currency": "usd",
            "days": 365
        }
    )

    if not data:
        return None

    prices = data.get("prices")

    if not prices:
        return None

    df = pd.DataFrame(
        prices,
        columns=["timestamp", "price"]
    )

    df.to_csv(
        filename,
        index=False
    )

    time.sleep(5)

    return df

# ==================================================
# METRICS
# ==================================================

def annual_return(df):

    start = df["price"].iloc[0]
    end = df["price"].iloc[-1]

    return (
        (end / start) - 1
    ) * 100


def returns_series(df):

    return (
        df["price"]
        .pct_change()
        .dropna()
    )


def sharpe_ratio(df):

    r = returns_series(df)

    if len(r) == 0:
        return 0

    std = r.std()

    if std == 0:
        return 0

    return (
        r.mean() / std
    ) * np.sqrt(365)


def max_drawdown(df):

    prices = df["price"]

    peak = prices.cummax()

    dd = (
        prices - peak
    ) / peak

    return dd.min() * 100


def volatility(df):

    r = returns_series(df)

    return (
        r.std()
        * np.sqrt(365)
        * 100
    )

# ==================================================
# SCORING
# ==================================================

def score_asset(
    annual_ret,
    sharpe,
    drawdown,
    relative
):

    score = 50

    score += annual_ret * 0.15

    score += sharpe * 8

    score += relative * 0.15

    score += drawdown * 0.05

    score = max(0, score)

    score = min(100, score)

    return round(score, 2)

# ==================================================
# RECOMMENDATIONS
# ==================================================

def recommendation(score):

    if score >= 90:
        return "ACCUMULATE"

    if score >= 75:
        return "KEEP"

    if score >= 50:
        return "WATCH"

    if score >= 25:
        return "REDUCE"

    return "SELL"

# ==================================================
# MAIN
# ==================================================

def main():

    if not os.path.exists(INPUT_FILE):

        print(
            f"Missing file: {INPUT_FILE}"
        )

        return

    holdings = pd.read_csv(INPUT_FILE)

    btc_history = load_history(BTC_ID)

    if btc_history is None:

        print(
            "Unable to load BTC history"
        )

        return

    btc_return = annual_return(
        btc_history
    )

    results = []

    for _, row in holdings.iterrows():

        original_symbol = str(
            row["Asset"]
        ).upper()

        quantity = float(
            row["Quantity"]
        )

        symbol = normalize_symbol(
            original_symbol
        )

        coin_id = COINGECKO_MAP.get(
            symbol
        )

        if coin_id is None:

            results.append(
                {
                    "Asset": original_symbol,
                    "Normalized": symbol,
                    "Score": 0,
                    "Recommendation": "UNMAPPED"
                }
            )

            continue

        history = load_history(
            coin_id
        )

        if history is None:

            results.append(
                {
                    "Asset": original_symbol,
                    "Normalized": symbol,
                    "Score": 0,
                    "Recommendation": "NO DATA"
                }
            )

            continue

        one_year_return = annual_return(
            history
        )

        sharpe = sharpe_ratio(
            history
        )

        drawdown = max_drawdown(
            history
        )

        relative_strength = (
            one_year_return
            - btc_return
        )

        score = score_asset(
            one_year_return,
            sharpe,
            drawdown,
            relative_strength
        )

        results.append(
            {
                "Asset": original_symbol,
                "Normalized": symbol,
                "Quantity": quantity,
                "1Y_Return": round(
                    one_year_return,
                    2
                ),
                "Sharpe": round(
                    sharpe,
                    2
                ),
                "Max_Drawdown": round(
                    drawdown,
                    2
                ),
                "Relative_vs_BTC": round(
                    relative_strength,
                    2
                ),
                "Score": score,
                "Recommendation":
                recommendation(score)
            }
        )

    report = pd.DataFrame(
        results
    )

    report = report.sort_values(
        by="Score",
        ascending=False
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nPORTFOLIO INTELLIGENCE REPORT V2")
    print("=" * 80)

    print(
        report[
            [
                "Asset",
                "Normalized",
                "Score",
                "Recommendation"
            ]
        ].head(50)
    )

    print(
        f"\nSaved: {OUTPUT_FILE}"
    )

# ==================================================

if __name__ == "__main__":
    main()