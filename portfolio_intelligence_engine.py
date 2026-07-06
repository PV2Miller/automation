import requests
import pandas as pd
import numpy as np
import time

INPUT_FILE = "kraken_balances_20260704_135003.csv"
OUTPUT_FILE = "portfolio_intelligence_report.csv"

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
    "TRX": "tron",
    "USDC": "usd-coin",
    "XAUT": "tether-gold",
    "XDC": "xdc-network",
    "ZRO": "layerzero"
}

BTC_ID = "bitcoin"


def safe_get(url, params=None):

    try:

        r = requests.get(
            url,
            params=params,
            timeout=30
        )

        if r.status_code != 200:
            print(f"HTTP {r.status_code}")
            return None

        return r.json()

    except Exception as e:

        print(e)

        return None


def get_history(coin_id):

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

    return df


def annual_return(df):

    start = df["price"].iloc[0]
    end = df["price"].iloc[-1]

    return ((end / start) - 1) * 100


def returns_series(df):

    return df["price"].pct_change().dropna()


def sharpe_ratio(df):

    r = returns_series(df)

    if len(r) == 0:
        return 0

    std = r.std()

    if std == 0:
        return 0

    return (r.mean() / std) * np.sqrt(365)


def volatility(df):

    r = returns_series(df)

    return r.std() * np.sqrt(365) * 100


def max_drawdown(df):

    prices = df["price"]

    rolling_max = prices.cummax()

    drawdowns = (
        prices - rolling_max
    ) / rolling_max

    return drawdowns.min() * 100


def relative_strength(asset_return, btc_return):

    return asset_return - btc_return


def score_asset(
    annual_ret,
    sharpe,
    drawdown,
    relative
):

    score = 50

    score += annual_ret * 0.20

    score += sharpe * 10

    score += relative * 0.20

    score += drawdown * 0.10

    score = max(0, min(100, score))

    return round(score, 2)


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


def evaluate_asset(
    symbol,
    quantity,
    btc_return
):

    coin_id = COINGECKO_MAP.get(symbol)

    if not coin_id:

        return {
            "Asset": symbol,
            "Quantity": quantity,
            "Score": 0,
            "Recommendation": "UNMAPPED"
        }

    print(f"Analyzing {symbol}")

    history = get_history(coin_id)

    if history is None:

        return {
            "Asset": symbol,
            "Quantity": quantity,
            "Score": 0,
            "Recommendation": "NO DATA"
        }

    ann_ret = annual_return(history)

    sharpe = sharpe_ratio(history)

    dd = max_drawdown(history)

    rel = relative_strength(
        ann_ret,
        btc_return
    )

    score = score_asset(
        ann_ret,
        sharpe,
        dd,
        rel
    )

    return {
        "Asset": symbol,
        "Quantity": quantity,
        "1Y_Return": round(ann_ret, 2),
        "Sharpe": round(sharpe, 2),
        "Max_Drawdown": round(dd, 2),
        "Relative_vs_BTC": round(rel, 2),
        "Score": score,
        "Recommendation": recommendation(score)
    }


def main():

    holdings = pd.read_csv(INPUT_FILE)

    btc_history = get_history(BTC_ID)

    btc_return = annual_return(
        btc_history
    )

    results = []

    for _, row in holdings.iterrows():

        asset = str(
            row["Asset"]
        ).upper()

        quantity = float(
            row["Quantity"]
        )

        result = evaluate_asset(
            asset,
            quantity,
            btc_return
        )

        results.append(result)

        time.sleep(1)

    report = pd.DataFrame(results)

    report = report.sort_values(
        by="Score",
        ascending=False
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nREPORT COMPLETE")

    print(
        report[
            [
                "Asset",
                "Score",
                "Recommendation"
            ]
        ].head(50)
    )

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()