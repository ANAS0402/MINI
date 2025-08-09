# analysis/technical.py
import pandas as pd
import pandas_ta as ta
import numpy as np

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['ema_50'] = ta.ema(df['close'], length=50)
    df['ema_200'] = ta.ema(df['close'], length=200)
    df['rsi'] = ta.rsi(df['close'], length=14)
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['vol_mean20'] = df['volume'].rolling(20).mean()
    df['vol_std20'] = df['volume'].rolling(20).std().fillna(0) + 1e-9
    df['vol_z'] = (df['volume'] - df['vol_mean20']) / df['vol_std20']
    return df.dropna()

def ta_signal(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    score = 0.0
    reasons = []
    # trend
    if last['ema_50'] > last['ema_200']:
        score += 0.5
        reasons.append('EMA50>EMA200')
    if last['close'] > last['ema_50']:
        score += 0.2
        reasons.append('Price>EMA50')
    # volume confirmation
    if last['vol_z'] > 1.5:
        score += 0.2
        reasons.append('Vol surge')
    # avoid insane overbought
    if last['rsi'] < 92:
        score += 0.1
    side = 'LONG' if score >= 0.6 else None
    return {'side': side, 'score': float(round(score,3)), 'reasons': reasons}
