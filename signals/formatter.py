# signals/formatter.py
from datetime import datetime

def format_vbnet(trade: dict, model_version='mini_aladdin_v0.1') -> str:
    ts = datetime.utcnow().isoformat() + 'Z'
    tp_str = ' / '.join([str(x) for x in trade['tp']])
    txt = f"""🧠 Mini Aladdin Trade Signal
Pair: [{trade['pair']}]
Type: [{trade['side']}]
Entry: [{trade['entry']}]
Stop Loss: [{trade['stop']}]
Take Profit: [{tp_str}]
Confidence: [{int(trade['confidence']*100)}%]
Reasoning: [{', '.join(trade.get('reasons', []))}]
Model Version: [{model_version}]
Timestamp (UTC): [{ts}]
"""
    return txt
