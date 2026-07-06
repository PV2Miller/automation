import pandas as pd
import os

# ==============================
# Portfolio Intelligence Engine
# Version 2
# ==============================

INPUT_FILE = "kraken_balances_20260704_135003.csv"
OUTPUT_FILE = "portfolio_report.csv"


def get_survivability_score(asset):
    """
    Basic survivability scoring.

    Version 2 placeholder.
    Future versions will use:
        - age
        - bear markets survived
        - market cap history
    """

    top_assets = {
        "BTC": 10,
        "ETH": 10,
        "SOL": 8,
        "ATOM": 8,
        "ADA": 8,
        "QNT": 9,
        "XMR": 9,
        "HBAR": 7,
        "TRX": 7,
        "XRP": 8
    }

    return top_assets.get(asset, 5)


def get_liquidity_score(asset):
    """
    Placeholder liquidity model.
    """

    high_liquidity = {
        "BTC",
        "ETH",
        "SOL",
        "ADA",
        "XRP",
        "TRX",
        "ATOM"
    }

    if asset in high_liquidity:
        return 10

    return 6


def get_staking_score(asset):
    """
    Placeholder staking model.
    """

    staking_assets = {
        "ATOM": 10,
        "ADA": 8,
        "SOL": 8,
        "HBAR": 5,
        "TRX": 6
    }

    return staking_assets.get(asset, 0)


def get_utility_score(asset):
    """
    Placeholder utility scoring.
    """

    utility_assets = {
        "QNT": 10,
        "ETH": 10,
        "BTC": 9,
        "ATOM": 8,
        "HBAR": 8,
        "XMR": 8
    }

    return utility_assets.get(asset, 5)


def get_recommendation(score):

    if score >= 90:
        return "ACCUMULATE"

    if score >= 75:
        return "KEEP"

    if score >= 50:
        return "WATCH"

    if score >= 25:
        return "REDUCE"

    return "SELL"


def evaluate_asset(asset, quantity):

    survivability = get_survivability_score(asset) * 3
    liquidity = get_liquidity_score(asset) * 2
    utility = get_utility_score(asset) * 2
    staking = get_staking_score(asset)

    score = (
        survivability
        + liquidity
        + utility
        + staking
    )

    score = min(score, 100)

    recommendation = get_recommendation(score)

    return {
        "Asset": asset,
        "Quantity": quantity,
        "Score": score,
        "Recommendation": recommendation
    }


def main():

    if not os.path.exists(INPUT_FILE):
        print(f"Missing file: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    results = []

    for _, row in df.iterrows():

        asset = str(row["Asset"]).strip().upper()

        quantity = float(row["Quantity"])

        evaluation = evaluate_asset(
            asset,
            quantity
        )

        results.append(evaluation)

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by="Score",
        ascending=False
    )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nPortfolio Intelligence Report")
    print("=" * 60)

    print(
        results_df[
            [
                "Asset",
                "Quantity",
                "Score",
                "Recommendation"
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()