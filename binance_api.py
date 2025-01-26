import requests
import time
import logging
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)

# In-memory cache for daily klines: key=(symbol, start_ts, end_ts, interval), value=list of klines
_KLINES_CACHE = {}

def fetch_historical_klines(symbol: str, start_time: int, end_time: int, interval="1d"):
    """
    Fetch daily candlestick data from Binance. 
    Cache in memory to reduce repeated API calls.
    """
    cache_key = (symbol, start_time, end_time, interval)
    if cache_key in _KLINES_CACHE:
        return _KLINES_CACHE[cache_key]

    url = "https://api.binance.com/api/v3/klines"
    limit = 1000
    all_klines = []
    current_start_time = start_time

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start_time,
            "endTime": end_time,
            "limit": limit
        }
        try:
            r = requests.get(url, params=params)
            data = r.json()

            # Check for Binance error
            if isinstance(data, dict) and data.get("code"):
                raise ValueError(f"Binance API error: {data}")

            if not data or not isinstance(data, list):
                break

            all_klines.extend(data)
            if len(data) < limit:
                # No more data
                break

            last_open_time = data[-1][0]
            # Move to the next day
            current_start_time = last_open_time + (24 * 60 * 60 * 1000)
            if current_start_time >= end_time:
                break

            # Sleep to avoid hitting rate limits
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            break

    _KLINES_CACHE[cache_key] = all_klines
    return all_klines

def get_daily_closing_prices(symbol: str, start_dt, end_dt):
    """Return dict of date_str -> closing_price in [start_dt, end_dt]."""
    start_ts = int(start_dt.timestamp() * 1000)
    end_ts = int(end_dt.timestamp() * 1000)
    klines = fetch_historical_klines(symbol, start_ts, end_ts, interval="1d")

    closing_prices = {}
    for k in klines:
        open_time_ms = k[0]
        close_price = float(k[4])
        open_date = datetime.utcfromtimestamp(open_time_ms / 1000).date()
        closing_prices[str(open_date)] = close_price

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
