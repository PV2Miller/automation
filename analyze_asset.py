print("SCRIPT STARTED")print://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    r = requests.get(url)
    print("Status:", r.status_code)
    print("Data:", r.json())

if __name__ == "__main__":
    print("MAIN RUNNING")

    test()


import requests
import sys

def test():
dd = drawdown(history)
    ath = ath_ratio(history)
    rsi_val = rsi(history)

    return f"""
Coin: {coin_id}
Price: {round(price,2)}

30-Day Change: {round(change*100,2)}%
Trend: {trend}

Drawdown: {round(dd*100,2)}%
ATH Ratio: {round(ath,2)}
RSI: {round(rsi_val,2)}
"""