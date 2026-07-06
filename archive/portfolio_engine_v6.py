print("PORTFOLIO ENGINE V6 STARTED")

import requests
import sys

# ======================================
# MAPPING
# ======================================
SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "CIK": "christ-is-king"
}

# ======================================
# SAFE REQUEST
# ======================================
def safe_get(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ======================================
# FETCH HISTORY
# ======================================
def fetch_history(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=30"
    data = safe_get(url)

    if not isinstance(data, dict):
        return None

    prices = data.get("prices")

    if not prices:
        return None

    return [p[1] for p in prices]

# ======================================
# FETCH PRICE (WITH FALLBACK)
# ======================================
def fetch_price(coin, history):

    # PRIMARY
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    data = safe_get(url)

    if isinstance(data, dict):
        price = data.get(coin, {}).get("usd")
        if price:
            return price

    # FALLBACK → last historical price
    if history:
        return history[-1]

    return None

# ======================================
# METRICS
# ======================================
def drawdown(data):
    return (data[-1] - max(data)) / max(data)

def ath_ratio(data):
    peak = max(data)
    return data[-1] / peak if peak else 0

def rsi(data, period=14):
    gains, losses = [], []

    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    if not gains or not losses:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ======================================
# ANALYSIS
# ======================================
def analyze(symbol):

    coin = SYMBOL_MAP.get(symbol.upper())

    if not coin:
        return f"\n{symbol} → NOT MAPPED\n"

    print(f"Resolved {symbol} → {coin}")

    history = fetch_history(coin)

    if history is None:
        return f"\n{symbol} → NO HISTORY DATA\n"

    price = fetch_price(coin, history)

    if price is None:
        return f"\n{symbol} → PRICE ERROR\n"

    change = (history[-1] - history[0]) / history[0]

    trend = "UP" if change > 0.05 else "DOWN" if change < -0.05 else "SIDEWAYS"

    dd = drawdown(history)
    ath = ath_ratio(history)
    rsi_val = rsi(history)

    if dd < -0.7:
        decision = "EXIT"
    elif change > 0.02:
        decision = "HOLD"
    elif change < -0.05:
        decision = "REDUCE"
    else:
        decision = "WATCH"

    return f"""
{symbol} ANALYSIS

Price: {round(price,2)}

30D Change: {round(change*100,2)}%
Trend: {trend}

Drawdown: {round(dd*100,2)}%
ATH Ratio: {round(ath,2)}
RSI: {round(rsi_val,2)}

Decision: {decision}
"""

# ======================================
# MAIN
# ======================================
if __name__ == "__main__":

    print("RUNNING PORTFOLIO...\n")

    if len(sys.argv) < 2:
        print("Usage: python portfolio_engine_v6.py BTC ETH SOL")
        sys.exit()

    for symbol in sys.argv[1:]:
        print(analyze(symbol))