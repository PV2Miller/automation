import json
import requests
import time

PORTFOLIO_PATH = r"C:\Automation\data\portfolio.json"

# =========================================================
# LOAD PORTFOLIO
# =========================================================
def load_portfolio():
    try:
        with open(PORTFOLIO_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print("DEBUG: Portfolio Loaded")
            return data
    except Exception as e:
        print("[ERROR] Failed to load portfolio:", e)
        return []

# =========================================================
# REAL MARKET DATA
# =========================================================
def get_market_data(asset):

    mapping = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana"
    }

    coin = mapping.get(asset)
    if not coin:
        return None, None

    try:
        time.sleep(1)

        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=5"
        data = requests.get(url).json()

        if "prices" not in data:
            return None, None

        prices = [p[1] for p in data["prices"]]

        history = prices[-5:]
        price = history[-1]

        return price, history

    except Exception as e:
        print(f"[WARNING] API issue for {asset}: {e}")
        return None, None

# =========================================================
# SIGNAL ENGINE (FIXED SCALING)
# =========================================================
def analyze(asset, price, history):

    avg = sum(history) / len(history)
    dev = (price - avg) / avg

    # ✅ FIXED signal thresholds (more realistic)
    if dev > 0.01:
        action = "HOLD"
        reason = "Above trend"
    elif dev < -0.02:
        action = "REDUCE"
        reason = "Below trend"
    else:
        action = "WATCH"
        reason = "No strong signal"

    # ✅ FIX: scale deviation properly
    confidence = min(abs(dev) * 150, 1.0)
    confidence = round(confidence, 2)

    return f"{asset} -> {action} | CONF {confidence} | {reason}"

# =========================================================
# OUTPUT
# =========================================================
def print_digest(results):

    print("\n==============================")
    print("CRMILLER DAILY DIGEST")
    print("==============================")

    for r in results:
        print(r)

    print("==============================")

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    print("STARTING SCRIPT")

    portfolio = load_portfolio()

    results = []

    for item in portfolio:
        asset = item["asset"]
        print("PROCESSING:", asset)

        price, history = get_market_data(asset)

        if price is None or history is None:
            results.append(f"{asset} -> DATA UNAVAILABLE")
            continue

        result = analyze(asset, price, history)
        results.append(result)

    print_digest(results)