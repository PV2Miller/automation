import pandas as pd
import numpy as np
import os

INPUT_FILE = "kraken_balances_20260704_135003.csv"
OUTPUT_FILE = "portfolio_intelligence_report.csv"


# ==========================================
# SCORING HELPERS
# ==========================================

def score_lifetime_performance(asset):
    """
    Placeholder until historical provider
    is finalized.

    Scale: 0-20
    """

    winners = {
        "BTC": 20,
        "ETH": 19,
        "QNT": 17,
        "ATOM": 15,
        "ADA": 14,
        "XMR": 18,
        "HBAR": 13,
        "SOL": 18
    }

    return winners.get(asset, 10)


def score_survivability(asset):
    """
    Scale: 0-15
    """

    survivors = {
        "BTC": 15,
        "ETH": 15,
        "XMR": 14,
        "ADA": 13,
        "ATOM": 12,
        "QNT": 12,
        "SOL": 10
    }

    return survivors.get(asset, 6)


def score_relative_strength(asset):
    """
    Placeholder for future BTC comparison.

    Scale: 0-15
    """

    leaders = {
        "BTC": 15,
        "ETH": 14,
        "QNT": 13,
        "SOL": 13,
        "ATOM": 11
    }

    return leaders.get(asset, 7)


def score_liquidity(asset):
    """
    Scale: 0-10
    """

    high_liquidity = {
        "BTC",
        "ETH",
        "SOL",
        "ADA",
        "ATOM",
        "XRP",
        "TRX"
    }

    if asset in high_liquidity:
        return 10

    return 5


def score_staking(asset):
    """
    Scale: 0-10
    """

    staking = {
        "ATOM": 10,
        "ADA": 8,
        "SOL": 8,
        "TRX": 6,
        "HBAR": 5
    }

    return staking.get(asset, 0)


def score_utility(asset):
    """
    Scale: 0-15
    """

    utility = {
        "QNT": 15,
        "ETH": 15,
        "BTC": 14,
        "ATOM": 12,
        "HBAR": 12,
        "XMR": 12
    }

    return utility.get(asset, 6)


# ==========================================
# FINAL RECOMMENDATION
# ==========================================

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


# ==========================================
# EVALUATION
# ==========================================

def evaluate(asset, quantity):

    lifetime = score_lifetime_performance(asset)

    survivability = score_survivability(asset)

    relative = score_relative_strength(asset)

    liquidity = score_liquidity(asset)

    staking = score_staking(asset)

    utility = score_utility(asset)

    total = (
        lifetime
        + survivability
        + relative
        + liquidity
        + staking
        + utility
    )

    total = min(total, 100)

    return {
        "Asset": asset,
        "Quantity": quantity,
        "Lifetime": lifetime,
        "Survivability": survivability,
        "RelativeStrength": relative,
        "Liquidity": liquidity,
        "Utility": utility,
        "Staking": staking,
        "TotalScore": total,
        "Recommendation": recommendation(total)
    }


# ==========================================
# MAIN
# ==========================================

def main():

    if not os.path.exists(INPUT_FILE):
        print(f"Missing file: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    report = []

    for _, row in df.iterrows():

        asset = str(row["Asset"]).upper().strip()

        quantity = float(row["Quantity"])

        result = evaluate(
            asset,
            quantity
        )

        report.append(result)

    results = pd.DataFrame(report)

    results = results.sort_values(
        by="TotalScore",
        ascending=False
    )

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nPORTFOLIO INTELLIGENCE REPORT")
    print("=" * 80)

    print(
        results[
            [
                "Asset",
                "TotalScore",
                "Recommendation"
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()