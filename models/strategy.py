# models/strategy.py
import numpy as np

def build_trade_from_signal(df, ta_out, funding_rate=None, onchain_score=None, confidence_threshold=0.6):
    last = df.iloc[-1]
    entry = float(last['close'])
    atr = float(last['atr']) if not np.isnan(last['atr']) else max(1.0, entry*0.01)

    # stops & tps using ATR
    if ta_out['side'] == 'LONG':
        stop = entry - 1.5 * atr
        tp1 = entry + 2 * atr
        tp2 = entry + 4 * atr
    else:
        return None

    # Compose scores
    w_ta = 0.6
    w_deriv = 0.2
    w_onchain = 0.2

    deriv_score = 0.5 if (funding_rate is None or funding_rate <= 0) else 0.0
    onchain_score = (onchain_score if onchain_score is not None else 0.5)

    confidence = w_ta * ta_out['score'] + w_deriv * deriv_score + w_onchain * onchain_score

    if ta_out['side'] is None or confidence < confidence_threshold:
        return None

    return {
        'pair': getattr(df, 'name', 'UNKNOWN'),
        'side': ta_out['side'],
        'entry': round(entry, 8),
        'stop': round(max(0, stop), 8),
        'tp': [round(tp1,8), round(tp2,8)],
        'confidence': round(float(confidence), 3),
        'reasons': ta_out.get('reasons', [])
    }
