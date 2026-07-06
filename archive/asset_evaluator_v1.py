import requests
import pandas as pd
import numpy as np


def get_market_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"

        response = requests.get(
            url,
            params={
                "vs_currency": "usd",
                "days": "max"
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"CoinGecko Error: {response.status_code}")
            return None

        data = response.json()

        prices = data.get("prices", [])

        if len(prices) < 10:
            print("Insufficient price history")
            return None

        df = pd.DataFrame(
            prices,
            columns=["timestamp", "price"]
        )

        df["date"] = pd.to_datetime(
            df["timestamp"],
            unit="ms"
        )

        return df

    except Exception as e:
        print("Market data error:", e)
        return None


def calculate_metrics(df):

    df = df.copy()

    df["returns"] = df["price"].pct_change()

    df.dropna(inplace=True)

    start_price = df["price"].iloc[0]
    end_price = df["price"].iloc[-1]

    lifetime_return = (
        end_price / start_price - 1
    ) * 100

    years = (
        (df["date"].iloc[-1] - df["date"].iloc[0]).days
        / 365.25
    )

    if years <= 0:
        cagr = 0
    else:
        cagr = (
            (end_price / start_price)
            ** (1 / years)
            - 1
        ) * 100

    volatility = df["returns"].std()

    if volatility == 0:
        sharpe = 0
    else:
        sharpe = (
            df["returns"].mean()
            / volatility
        ) * np.sqrt(365)

    downside = df["returns"][df["returns"] < 0]

    if len(downside) == 0:
        sortino = sharpe
    else:
        downside_std = downside.std()

        if downside_std == 0:
            sortino = sharpe
        else:
            sortino = (
                df["returns"].mean()
                / downside_std
            ) * np.sqrt(365)

    rolling_max = df["price"].cummax()

    drawdown = (
        (df["price"] - rolling_max)
        / rolling_max
    )

    max_drawdown = drawdown.min() * 100

    return {
        "Lifetime Return %": round(lifetime_return, 2),
        "CAGR %": round(cagr, 2),
        "Sharpe Ratio": round(sharpe, 2),
        "Sortino Ratio": round(sortino, 2),
        "Max Drawdown %": round(max_drawdown, 2)
    }


def evaluate_asset(name, coin_id):

    print(f"\nEvaluating {name}")
    print("-" * 50)

    df = get_market_data(coin_id)

    if df is None:
        print("Unable to retrieve market data.")
        return

    metrics = calculate_metrics(df)

    for key, value in metrics.items():
        print(f"{key}: {value}")

    print("\nEvaluation Complete")


if __name__ == "__main__":

    evaluate_asset(
        "Bitcoin",
        "bitcoin"
    )