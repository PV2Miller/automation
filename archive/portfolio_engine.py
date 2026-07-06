print("PORTFOLIO ENGINE STARTED")

import requests
import sys

# ======================================
# FIND COIN ID BY SYMBOL
# ======================================
def find_coin_id(symbol):

    url = "https://api.coingecko.com/api/v3/coins/list"
    data = requests.get(url).json()

    symbol = symbol.lower()

    for coin in data:
        if coin["symbol"] == symbol:
            return coin["id"]

    return None

# ======================================
# FETCH PRICE
# ======================================
def fetch_price(coin):

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    data = r.json()

    if coin not in data:
        return None

    return data[coin]["usd"]

# ======================================
# FETCH HISTORY
# ======================================
def fetch_history(coin):

    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=30"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    return [p[1] for p in r.json()["prices"]]

# ======================================
# METRICS
# ======================================
def drawdown(data):
    peak = max(data)
    return (data[-1] - peak) / peak

def ath_ratio(data):
    peak = max(data)
    return data[-1] / peak if peak else 0

def rsi(data, period=14):

    gains = []
    losses = []

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
# ANALYZE
# ======================================
def analyze(symbol):

    coin_id = find_coin_id(symbol)

    if not coin_id:
        return f"\n{symbol.upper()} → NOT FOUND (HIGH RISK)\n"

    price = fetch_price(coin_id)
    history = fetch_history(coin_id)

    if price is None or history is None:
        return f"\n{symbol.upper()} → DATA ERROR\n"

    change = (history[-1] - history[0]) / history[0]

    if change > 0.05:
        trend = "UP"
    elif change < -0.05:
        trend = "DOWN"
    else:
        trend = "SIDEWAYS"

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
{symbol.upper()} ANALYSIS

Coin ID: {coin_id}
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
        print("Usage: python portfolio_engine.py BTC ETH SOL")
        sys.exit()

    coins = sys.argv[1:]

    for c in coins:
        print(analyze(c))
