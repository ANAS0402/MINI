# analysis/derivatives.py
def fetch_funding_rate(exchange, symbol):
    try:
        if hasattr(exchange, 'fetch_funding_rate'):
            fr = exchange.fetch_funding_rate(symbol)
            # ccxt uses 'fundingRate' key often; fallback to 0
            return float(fr.get('fundingRate', 0.0)) if fr else None
        # fallback: try symbol-specific endpoints or return None
        return None
    except Exception:
        return None
