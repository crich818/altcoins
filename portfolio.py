import pandas as pd
import matplotlib.pyplot as plt
import ccxt
from datetime import datetime
import time

## Input current holdings and weight
portfolio_base = [
    ("SQD", 91343, 0.16, 0.24, "SQD/USDT"),
    ("GRASS", 120000, 1.81, 1.84, "GRASS/USDT"),
    ("SYRUP", 47756, 0.21, 0.406, "SYRUP/USDT"),
    ("INIT", 300000, 0.86, 0.75, "INIT/USDT"),
    ("VIRTUALS", 200000, 1.84, 1.88, "VIRTUAL/USDT"),
    ("COOKIE", 100000, 0.25, 0.22, "COOKIE/USDT")
]

## Add Additional Headers
df_portfolio = pd.DataFrame(portfolio_base, columns=["Token", "Number of Holdings", "Average Price", "Current Price", "CCXT Symbol"])
df_portfolio['% Return'] = (df_portfolio['Current Price'] - df_portfolio['Average Price']) / df_portfolio['Average Price']
df_portfolio["Cost Basis"] = df_portfolio["Number of Holdings"] * df_portfolio["Average Price"]
df_portfolio['Current Value'] = df_portfolio['Number of Holdings'] * df_portfolio["Current Price"]
df_portfolio["$ Return"] = df_portfolio["Current Value"] - df_portfolio["Cost Basis"]
df_portfolio["% Return"] = (df_portfolio["$ Return"] / df_portfolio["Cost Basis"]) * 100

# Create Total Row
total_row = {
    "Token": "TOTAL",
    "Number of Holdings": df_portfolio["Number of Holdings"].sum(),
    "Average Price": "",  # Not meaningful to sum
    "Current Price": "",  # Not meaningful to sum
    "CCXT Symbol": "",
    "Cost Basis": df_portfolio["Cost Basis"].sum(),
    "Current Value": df_portfolio["Current Value"].sum(),
    "$ Return": df_portfolio["$ Return"].sum(),
    "% Return": (df_portfolio["$ Return"].sum() / df_portfolio["Cost Basis"].sum()) * 100
}

# Append total row to DataFrame
df_portfolio = pd.concat([df_portfolio, pd.DataFrame([total_row])], ignore_index=True)

# Initialize Gate.io
exchange = ccxt.gateio()
markets = exchange.load_markets()

# Convert to DataFrame
df_portfolio = pd.DataFrame(portfolio_base, columns=["Token", "Holdings", "Avg Price", "Current Price", "CCXT Symbol"])

# Fetch and normalize each token’s value over time
price_data = {}
for _, row in df_portfolio.iterrows():
    symbol = row["CCXT Symbol"]
    token = row["Token"]
    
    if symbol not in markets:
        print(f"❌ Not on Gate.io: {symbol}")
        continue

    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=60)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
        df.set_index("timestamp", inplace=True)

        # Calculate daily USD value of position
        value_series = df["close"] * row["Holdings"]

        # Normalize to % change from day 0
        value_pct_change = (value_series / value_series.iloc[0] - 1) * 100
        price_data[token] = value_pct_change

        time.sleep(exchange.rateLimit / 1000)
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")

# Combine and compute portfolio-wide average % return
df_returns = pd.DataFrame(price_data)
df_returns["Portfolio % Return"] = df_returns.mean(axis=1)

# Plot all lines
plt.figure(figsize=(14, 7))
for column in df_returns.columns:
    plt.plot(df_returns.index, df_returns[column], label=column, linewidth=2 if "Portfolio" in column else 1)

plt.title("📈 Normalized % Return Over Last 60 Days (Each Token + Portfolio)")
plt.xlabel("Date")
plt.ylabel("% Return")
plt.axhline(0, color='gray', linestyle='--')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()







# Now Add in the old portfolio

portfolio_old = [
    ("FWOG", ),
    ("DESTRA", ),
    ("XAI", 15000000, 0.),
    ("LAUNCHCOIN", 5000000, 0.22, 0.18),
    ("SOON", 150000, 0.52, 0.39 ),
    ("GEOD", )
]

df_portfolio_old = pd.DataFrame(portfolio_old, columns=["Token", "Number of Holdings", "Average Price", "Sale Price", "CCXT Symbol"])


portfolio_hedge = [
    ("SUI", 150000, 3.6, 3.2, "SUI/USDT"),
    ("HYPE", 2000, 38.5, 36, "HYPE/USDT")
]

df_portfolio_hedge = pd.DataFrame(portfolio_hedge, columns=["Token", "Number of Holdings", "Average Price", "Market Price", "CCXT Symbol"])


# Create a weighted top 10 average basket as short
portfolio_hedge_index = [
    ("BTC"),
    ("ETH"),
    ("SOL"),
    ("")
]



# This is old histogram of returns
#plt.figure(figsize=(10, 6))
#plt.bar(df_portfolio['Token'], df_portfolio['% Return'])
#plt.title("Token % Return")
#plt.xlabel("Token")
#plt.ylabel("% Return")
#plt.grid(True)
#plt.show()

#print(df_portfolio)