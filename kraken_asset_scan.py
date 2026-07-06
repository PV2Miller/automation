import os
from dotenv import load_dotenv
import krakenex
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError(
        "Missing KRAKEN_API_KEY or KRAKEN_API_SECRET in .env file"
    )

# Connect to Kraken
api = krakenex.API(
    key=API_KEY,
    secret=API_SECRET
)

print("\nConnecting to Kraken...")

# Verify account access
balance_response = api.query_private("Balance")

if balance_response.get("error"):
    raise Exception(balance_response["error"])

print("Connected successfully.\n")

# Display balances
balances = balance_response["result"]

print("Portfolio Balances")
print("-" * 50)

rows = []

for asset, quantity in balances.items():
    try:
        qty = float(quantity)

        if qty > 0:
            rows.append(
                {
                    "Asset": asset,
                    "Quantity": qty
                }
            )

            print(f"{asset:<10} {qty}")

    except Exception:
        pass

portfolio_df = pd.DataFrame(rows)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

csv_file = f"kraken_balances_{timestamp}.csv"

portfolio_df.to_csv(csv_file, index=False)

print("\nSaved:")
print(csv_file)

# Pull all tradable pairs
pairs_response = api.query_public("AssetPairs")

if pairs_response.get("error"):
    raise Exception(pairs_response["error"])

pairs = pairs_response["result"]

assets = set()

for _, info in pairs.items():
    base_asset = info.get("base")

    if base_asset:
        assets.add(base_asset)

asset_list = sorted(list(assets))

print(f"\nTradable Assets Found: {len(asset_list)}")

assets_file = "kraken_assets.txt"

with open(assets_file, "w") as f:
    for asset in asset_list:
        f.write(asset + "\n")

print(f"Saved: {assets_file}")

print("\nTop 50 Assets")

for asset in asset_list[:50]:
    print(asset)