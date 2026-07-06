print("SCRIPT STARTED")

import requests

r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")

print(r.status_code)
print(r.text)

def sma(data):def sma) / len(data)

def roc(data):
    return (data[-1] - data[0]) / data[0]
def fetch_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    r = requests.get(url)

    if r.status_code != 200:
        print("History fetch failed")
        return None

    return [p[1] for p in r.json()["prices"]]