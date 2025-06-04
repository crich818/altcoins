import ccxt

exchange = ccxt.gateio()
markets = exchange.load_markets()

# Find all USDT spot pairs and check your tokens
token_list = ["SQD", "GRASS", "SYRUP", "INIT", "VIRTUAL", "COOKIE"]

for token in token_list:
    pair = f"{token}/USDT"
    if pair in markets:
        print(f"✅ Found: {pair}")
    else:
        # Try lowercase format (Gate.io sometimes uses lowercase like syrup_usdt)
        alt_symbol = f"{token.lower()}/usdt"
        if alt_symbol in markets:
            print(f"✅ Found alt case: {alt_symbol}")
        else:
            print(f"❌ Not found: {pair}")
