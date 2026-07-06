import requests
import pandas as pd


def search_coin(symbol):
    """
    Find CoinGecko coin ID from a symbol.
    """

    try:

        response = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": symbol},
            timeout=15
        )

        if response.status_code != 200:
            print(f"Search Error: {response.status_code}")
            return None

        data = response.json()

        coins = data.get("coins", [])

        if not coins:
            return None

        return coins[0]["id"]

    except Exception as e:
        print("Search exception:", e)
        return None


def get_price_history(coin_id):

    try:

        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={
                "vs_currency": "usd",
                "days": 365
            },
            timeout=30
        )

        print(
            f"\n{coin_id} status: "
            f"{response.status_code}"
        )

        if response.status_code != 200:
            print(response.text[:300])
            return None

        data = response.json()

        prices = data.get("prices", [])

        print(
            f"Price records returned: "
            f"{len(prices)}"
        )

        return prices

    except Exception as e:
        print("History exception:", e)
        return None


def main():

    coins = [
        "bitcoin",
        "ethereum",
        "solana"
    ]

    for coin in coins:

        get_price_history(coin)


if __name__ == "__main__":
    main()