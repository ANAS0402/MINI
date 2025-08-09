# main.py
import os
import json
import threading
import time
import logging

from flask import Flask, jsonify
from data_feeds.binance_feed import BinanceFeed
from analysis.technical import compute_indicators, ta_signal
from analysis.derivatives import fetch_funding_rate
from models.strategy import build_trade_from_signal
from models.backtest import simple_event_backtest
from signals.formatter import format_vbnet
from signals.telegram_bot import send_telegram_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mini_aladdin')

# Load config: prefer env vars then config/settings.json
def load_local_config():
    cfg = {}
    try:
        with open('config/settings.json') as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    return cfg

LOCAL_CFG = load_local_config()

# env helpers
def getenv_bool(k, default=False):
    v = os.environ.get(k)
    if v is None:
        return LOCAL_CFG.get(k, default)
    return str(v).lower() in ["1","true","yes","on"]

def getenv_str(k, default=None):
    return os.environ.get(k, LOCAL_CFG.get(k, default))

def getenv_int(k, default):
    v = os.environ.get(k)
    if v is None:
        return LOCAL_CFG.get(k, default)
    try:
        return int(v)
    except:
        return default

# essential envs
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_SECRET = os.environ.get('BINANCE_SECRET')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
SYMBOLS = os.environ.get('SYMBOLS', ','.join(LOCAL_CFG.get('SYMBOLS', ['BTC/USDT','ETH/USDT']))).split(',')
TIMEFRAME = getenv_str('TIMEFRAME', LOCAL_CFG.get('TIMEFRAME','1h'))
INTERVAL_SECONDS = getenv_int('INTERVAL_SECONDS', LOCAL_CFG.get('INTERVAL_SECONDS', 900))
PAPER_MODE = getenv_bool('PAPER_MODE', LOCAL_CFG.get('PAPER_MODE', True))
CONF_THRESH = float(os.environ.get('CONFIDENCE_THRESHOLD', LOCAL_CFG.get('CONFIDENCE_THRESHOLD', 0.6)))

logger.info(f"Symbols: {SYMBOLS}, timeframe: {TIMEFRAME}, interval: {INTERVAL_SECONDS}s, paper: {PAPER_MODE}")

feed = BinanceFeed(BINANCE_API_KEY, BINANCE_SECRET)
app = Flask(__name__)

def scan_and_publish_once():
    for symbol in SYMBOLS:
        try:
            logger.info(f"Scanning {symbol}")
            df = feed.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=500)
            df.name = symbol
            df = compute_indicators(df)
            ta_out = ta_signal(df)
            # attempt funding rate
            try:
                fr = fetch_funding_rate(feed.ex, symbol.replace('/',''))
            except Exception:
                fr = None
            trade = build_trade_from_signal(df, ta_out, funding_rate=fr, onchain_score=None, confidence_threshold=CONF_THRESH)
            if trade:
                logger.info("Candidate: %s", trade)
                # quick naive backtest sanity (last index)
                entry_idx = len(df)-1
                back = simple_event_backtest(df[['high','low','close']], entry_idx, trade['stop'], trade['tp'])
                msg = format_vbnet(trade)
                logger.info("Message:\n%s", msg)
                if not PAPER_MODE and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                    res = send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
                    logger.info("Telegram result: %s", res)
                else:
                    logger.info("PAPER MODE ON or telegram not configured — not sending.")
            else:
                logger.info("No trade for %s", symbol)
        except Exception as e:
            logger.exception("Error scanning %s: %s", symbol, str(e))

def scheduler_loop():
    logger.info("Scheduler thread started")
    while True:
        try:
            scan_and_publish_once()
        except Exception as e:
            logger.exception("Scheduler error: %s", str(e))
        time.sleep(INTERVAL_SECONDS)

# Start background scheduler thread when the module imports (works in Gunicorn too)
if os.environ.get('RUN_SCHEDULER', 'true').lower() in ['1','true','yes','on']:
    t = threading.Thread(target=scheduler_loop, daemon=True, name="mini-aladdin-scheduler")
    t.start()

@app.route('/')
def index():
    return jsonify({"status":"ok","service":"mini_aladdin","symbols":SYMBOLS})

@app.route('/health')
def health():
    return jsonify({"status":"healthy"})


if __name__ == '__main__':
    # local dev run
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
