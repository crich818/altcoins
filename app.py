import ccxt
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import time

st.set_page_config(layout="wide")
st.title("📈 Altcoin Portfolio Tracker (Gate.io, 30-Day Return + Hedge Option)")

# -------------------------------
# Step 1: Portfolio Base Data
# -------------------------------
portfolio_base = [
    ("SQD", 91343, 0.16, 0.24, "SQD/USDT"),
    ("GRASS", 120000, 1.81, 1.84, "GRASS/USDT"),
    ("SYRUP", 47756, 0.21, 0.406, "SYRUP/USDT"),
    ("INIT", 300000, 0.86, 0.75, "INIT/USDT"),
    ("VIRTUALS", 200000, 1.84, 1.88, "VIRTUAL/USDT"),
    ("COOKIE", 100000, 0.25, 0.22, "COOKIE/USDT")
]

df_portfolio = pd.DataFrame(portfolio_base, columns=["Token", "Holdings", "Avg Price", "Current Price", "CCXT Symbol"])

st.subheader("📋 Current Portfolio Inputs")
st.dataframe(df_portfolio.set_index("Token"))

# -------------------------------
# Step 2: Sidebar Controls
# -------------------------------
if "manual_weights" not in st.session_state:
    st.session_state.manual_weights = {token: 10 for token in df_portfolio["Token"]}

st.sidebar.header("🔧 Portfolio Controls")
mode = st.sidebar.radio("Weighting mode:", ["Equal Weight", "Manual Weight"])
show_hedge = st.sidebar.checkbox("Show Hedged Performance", value=False)

user_weights = {}
if mode == "Equal Weight":
    equal_weight = 100 / len(df_portfolio)
    for token in df_portfolio["Token"]:
        user_weights[token] = equal_weight
else:
    st.sidebar.markdown("Set token weights (%):")
    if st.sidebar.button("🔁 Reset to 10% Each"):
        st.session_state.manual_weights = {token: 10 for token in df_portfolio["Token"]}
    for token in df_portfolio["Token"]:
        st.session_state.manual_weights[token] = st.sidebar.slider(
            f"{token}", 0, 100, st.session_state.manual_weights[token]
        )
        user_weights[token] = st.session_state.manual_weights[token]

# Normalize weights
total_weight = sum(user_weights.values())
weights_normalized = {k: v / total_weight if total_weight > 0 else 0 for k, v in user_weights.items()}

# -------------------------------
# Step 3: Run Analysis
# -------------------------------
if st.button("🚀 Run 30-Day Performance Analysis"):

    st.write("Fetching prices from Gate.io...")
    exchange = ccxt.gateio()
    markets = exchange.load_markets()

    # Portfolio price data
    price_data = {}
    latest_values = {}
    progress = st.progress(0)

    for i, row in df_portfolio.iterrows():
        symbol = row["CCXT Symbol"]
        token = row["Token"]
        holdings = row["Holdings"]

        progress.progress((i + 1) / len(df_portfolio))

        if symbol not in markets:
            st.warning(f"{symbol} not listed on Gate.io.")
            continue

        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=30)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
            df.set_index("timestamp", inplace=True)

            value_series = df["close"] * holdings
            pct_change = (value_series / value_series.iloc[0] - 1) * 100
            price_data[token] = pct_change

            latest_values[token] = value_series.iloc[-1]
            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            st.error(f"Error fetching {symbol}: {e}")

    df_returns = pd.DataFrame(price_data)

    if not df_returns.empty:
        df_returns["Portfolio % Return (Weighted)"] = sum(
            df_returns[token] * weights_normalized[token] for token in df_returns.columns if token in weights_normalized
        )

        # -------------------------------
        # Step 4: Optional Hedge Mode
        # -------------------------------
        if show_hedge:
            st.write("📉 Loading top 5 hedge basket: BTC, ETH, SOL, BNB, XRP (equal short)")
            hedge_symbols = {
                "BTC": "BTC/USDT",
                "ETH": "ETH/USDT",
                "SOL": "SOL/USDT",
                "BNB": "BNB/USDT",
                "XRP": "XRP/USDT"
            }

            hedge_returns = {}
            for name, symbol in hedge_symbols.items():
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=30)
                    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
                    df.set_index("timestamp", inplace=True)

                    pct_change = (df["close"] / df["close"].iloc[0] - 1) * 100
                    hedge_returns[name] = pct_change

                    time.sleep(exchange.rateLimit / 1000)
                except Exception as e:
                    st.error(f"Failed to fetch hedge asset {symbol}: {e}")

            df_hedge = pd.DataFrame(hedge_returns)
            df_hedge["Hedge Basket Return"] = df_hedge.mean(axis=1)
            df_returns["Portfolio (Hedged)"] = df_returns["Portfolio % Return (Weighted)"] - df_hedge["Hedge Basket Return"]

        # -------------------------------
        # Step 5: Charts and Tables
        # -------------------------------
        st.subheader("📊 % Return Over Last 30 Days")
        st.line_chart(df_returns)

        st.subheader("📋 Latest % Return Snapshot")
        latest = df_returns.iloc[-1].sort_values(ascending=False).round(2)
        st.dataframe(latest.to_frame("Latest % Return"))

        st.subheader("💰 Current Portfolio Value (Weighted in USDT)")
        weighted_values = {
            token: latest_values[token] * weights_normalized[token] for token in latest_values if token in weights_normalized
        }
        total_value = sum(weighted_values.values())

        df_val = pd.DataFrame([
            {"Token": token, "Value (USDT)": v, "Weight (%)": round(weights_normalized[token] * 100, 2)}
            for token, v in weighted_values.items()
        ])
        df_val = df_val.sort_values(by="Value (USDT)", ascending=False)
        st.dataframe(df_val.set_index("Token"))
        st.metric(label="Total Portfolio Value (USDT)", value=f"${total_value:,.2f}")
    else:
        st.error("❌ No data returned. Check your token symbols or try again.")

else:
    st.info("👇 Choose a weighting mode and press **Run Analysis** to see returns.")
