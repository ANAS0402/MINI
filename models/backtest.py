# models/backtest.py
def simple_event_backtest(prices, entry_idx, stop_price, tp_prices, horizon=48):
    # prices: DataFrame with ['high','low','close']
    out = {'hit': None, 'hit_price': None, 'bars_to_hit': None}
    end = min(len(prices)-1, entry_idx + horizon)
    for i in range(entry_idx+1, end+1):
        row = prices.iloc[i]
        # Check TP first (LONG)
        if row['high'] >= tp_prices[0]:
            out['hit'] = 'TP1'
            out['hit_price'] = tp_prices[0]
            out['bars_to_hit'] = i - entry_idx
            return out
        if row['low'] <= stop_price:
            out['hit'] = 'STOP'
            out['hit_price'] = stop_price
            out['bars_to_hit'] = i - entry_idx
            return out
    return out
