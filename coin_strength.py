import requests
import pandas as pd
import numpy as np


def get_data(name):
    try:
        # Search coin on CoinGecko
        search = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": name}
        ).json()

        coins = search.get("coins", [])
        if not coins:
            return None

        coin_id = coins[0]["id"]

        # Get price history
        data = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": 1}
        ).json()

        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])

        if not prices:
            return None

        df = pd.DataFrame(prices, columns=["time", "price"])
        df["volume"] = [v[1] for v in volumes]
        df["time"] = pd.to_datetime(df["time"], unit="ms")

        return df

    except Exception as e:
        print("Error getting data:", e)
        return None


def calculate_strength(df):
    if df is None or len(df) < 3:
        return None

    df["returns"] = df["price"].pct_change()

    momentum = df["price"].iloc[-1] / df["price"].iloc[0] - 1
    volume = df["volume"].mean()
    volatility = df["returns"].std()

    score = (momentum * 100) - volatility

    return round(score, 2)


def evaluate_coin(name):
    print(f"\n🔍 Searching: {name}")

    df = get_data(name)

    if df is None:
        print("❌ No data found")
        return

    strength = calculate_strength(df)

    print(f"🔥 Strength: {strength}")

    if strength > 5:
        signal = "🚀 STRONG BUY"
    elif strength > 1:
        signal = "✅ BUY"
    elif strength < 0:
        signal = "⚠️ WEAK"
    else:
        signal = "➖ NEUTRAL"

    print(f"📢 Signal: {signal}")


if __name__ == "__main__":
    coin = input("Enter coin name: ")
    evaluate_coin(coin)