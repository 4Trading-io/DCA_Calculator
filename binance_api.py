# binance_api.py

import requests
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Simple in-memory cache: (symbol, start_ts, end_ts, interval) -> list of klines
_KLINES_CACHE = {}

def fetch_historical_klines(symbol: str, start_ts: int, end_ts: int, interval="1d"):
    """
    Fetch candlestick data from Binance for a given symbol and interval ("1h", "1d", etc.)
    Returns a list of raw klines.

    We do simple caching to avoid repeated calls. If you want more robust caching,
    consider a database or redis approach.
    """
    cache_key = (symbol, start_ts, end_ts, interval)
    if cache_key in _KLINES_CACHE:
        return _KLINES_CACHE[cache_key]

    url = "https://api.binance.com/api/v3/klines"
    limit = 1000
    all_klines = []
    current_start = start_ts

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,   # "1h" or "1d" etc.
            "startTime": current_start,
            "endTime": end_ts,
            "limit": limit
        }
        try:
            resp = requests.get(url, params=params)
            data = resp.json()

            if isinstance(data, dict) and data.get("code"):
                raise ValueError(f"Binance API error: {data}")

            if not data or not isinstance(data, list):
                break

            all_klines.extend(data)
            if len(data) < limit:
                # done
                break

            last_open_time = data[-1][0]  # ms
            # Step forward by the interval. For "1h", we add 1 hour in ms; for "1d", 1 day in ms, etc.
            if interval.endswith("h"):
                # e.g. "1h" => 1 hour, "2h" => 2 hours
                hours_val = int(interval.replace("h", ""))  # handle "1h", "2h", etc.
                current_start = last_open_time + (hours_val * 3600 * 1000)
            else:
                # default daily => 24 hours
                current_start = last_open_time + (24 * 3600 * 1000)

            if current_start >= end_ts:
                break

            # short delay to avoid hitting rate limits too fast
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            break

    _KLINES_CACHE[cache_key] = all_klines
    return all_klines

def get_closing_prices(symbol, start_dt, end_dt, interval="1d"):
    """
    Return a dict: {time_key -> close_price}

    If interval="1h", keys are "YYYY-MM-DD HH"
    If interval="1d", keys are "YYYY-MM-DD"
    """
    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)

    klines = fetch_historical_klines(symbol, start_ts, end_ts, interval)

    closing_prices = {}
    for k in klines:
        open_ms = k[0]
        close_price = float(k[4])

        if interval.endswith("h"):
            # store as "YYYY-MM-DD HH"
            dt_key = datetime.utcfromtimestamp(open_ms/1000).strftime("%Y-%m-%d %H")
        else:
            # daily => "YYYY-MM-DD"
            dt_key = datetime.utcfromtimestamp(open_ms/1000).strftime("%Y-%m-%d")

        closing_prices[dt_key] = close_price

    return closing_prices

def fetch_current_price(symbol: str) -> float:
    """
    Fetch the latest market price for a symbol from Binance.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    r = requests.get(url, params=params)
    data = r.json()
    if "price" in data:
        return float(data["price"])
    raise ValueError(f"Could not fetch current price for {symbol}")
