# data_feeds/binance_feed.py
import ccxt
import pandas as pd
import time
import os

class BinanceFeed:
    def __init__(self, api_key=None, secret=None):
        kwargs = {"enableRateLimit": True}
        if api_key and secret:
            kwargs.update({"apiKey": api_key, "secret": secret})
        self.ex = ccxt.binance(kwargs)

    def fetch_ohlcv(self, symbol="BTC/USDT", timeframe="1h", limit=500):
        tries = 0
        while True:
            try:
                ohlcv = self.ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df.set_index("timestamp", inplace=True)
                return df
            except Exception as e:
                tries += 1
                if tries > 3:
                    raise
                time.sleep(1)

    def fetch_order_book(self, symbol="BTC/USDT", limit=50):
        return self.ex.fetch_order_book(symbol, limit=limit)

    def fetch_recent_trades(self, symbol="BTC/USDT", limit=100):
        return self.ex.fetch_trades(symbol, limit=limit)
