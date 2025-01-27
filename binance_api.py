# binance_api.py

import requests
import time
import logging
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)

_KLINES_CACHE = {}  # (symbol, start_ts, end_ts, interval) -> list of klines

def fetch_historical_klines(symbol: str, start_time: int, end_time: int, kline_interval="1d"):
    """
    Fetch candlestick data from Binance with a given interval (e.g., '1h', '1d').
    Cache results to avoid repeated calls.
    """
    cache_key = (symbol, start_time, end_time, kline_interval)
    if cache_key in _KLINES_CACHE:
        return _KLINES_CACHE[cache_key]

    url = "https://api.binance.com/api/v3/klines"
    limit = 1000
    all_klines = []
    current_start_time = start_time

    while True:
        params = {
            "symbol": symbol,
            "interval": kline_interval,
            "startTime": current_start_time,
            "endTime": end_time,
            "limit": limit
        }
        try:
            r = requests.get(url, params=params)
            data = r.json()

            if isinstance(data, dict) and data.get("code"):
                raise ValueError(f"Binance API error: {data}")

            if not data or not isinstance(data, list):
                break

            all_klines.extend(data)
            if len(data) < limit:
                # no more data
                break

            last_open_time = data[-1][0]
            # increment by interval in milliseconds
            if kline_interval.endswith("h"):
                # 1 hour => 3600 * 1000 ms
                hours = int(kline_interval.replace("h", ""))  # e.g. "1h" -> 1
                current_start_time = last_open_time + (hours * 3600 * 1000)
            else:
                # daily => 24 * 3600 * 1000
                current_start_time = last_open_time + (24 * 3600 * 1000)

            if current_start_time >= end_time:
                break

            time.sleep(0.1)  # small pause to avoid rate limits
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            break

    _KLINES_CACHE[cache_key] = all_klines
    return all_klines

def get_closing_prices(symbol: str, start_dt, end_dt, kline_interval="1d"):
    """
    Return a dict of date/time_str -> closing_price
    - If 'kline_interval' is '1h', use date+hour
    - If '1d', use date only
    """
    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)
    klines = fetch_historical_klines(symbol, start_ts, end_ts, kline_interval)

    closing_prices = {}
    for k in klines:
        open_time_ms = k[0]
        close_price = float(k[4])

        # If 1h, let's store full "YYYY-MM-DD HH" key
        # If 1d, store just "YYYY-MM-DD"
        if kline_interval.endswith("h"):
            dt_str = datetime.utcfromtimestamp(open_time_ms/1000).strftime("%Y-%m-%d %H")
        else:
            dt_str = datetime.utcfromtimestamp(open_time_ms/1000).strftime("%Y-%m-%d")

        closing_prices[dt_str] = close_price

    return closing_prices

@lru_cache(maxsize=128)
def fetch_current_price(symbol: str) -> float:
    """Fetch current price from Binance (cached)."""
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    r = requests.get(url, params=params)
    data = r.json()
    if "price" in data:
        return float(data["price"])
    raise ValueError(f"Could not fetch current price for {symbol}")
