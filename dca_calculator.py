# dca_calculator.py

import math
import logging
from datetime import datetime, timedelta

# We'll assume you have a binance_api.py with a function:
#   get_closing_prices(symbol, start_dt, end_dt, interval="1d")
# that returns a dict of:
#   key -> close_price
#   If interval="1h", key might be "YYYY-MM-DD HH"
#   If interval="1d", key might be "YYYY-MM-DD"
#
# and a function fetch_current_price(symbol)
from binance_api import get_closing_prices, fetch_current_price

logger = logging.getLogger(__name__)

def persian_to_ascii(text: str) -> str:
    """
    Convert Persian digits to ASCII digits,
    and also do some replacements to help parse time units in Farsi
    for both period (سال, ماه, etc.) and frequency (روزانه, ساعتی, etc.).
    """
    digits_map = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for p_digit, en_digit in digits_map.items():
        text = text.replace(p_digit, en_digit)

    # Farsi words for frequencies => approximate English
    # "ساعتی" => "hourly"
    text = text.replace('ساعتی', 'hourly')
    text = text.replace('هفتگی', 'weekly')
    text = text.replace('هر دو هفته', 'biweekly')
    text = text.replace('ماهانه', 'monthly')
    text = text.replace('ماهیانه', 'monthly')
    text = text.replace('روزانه', 'daily')

    # "هر X ساعت" => "every X hour"
    text = text.replace('ساعت', 'hour')
    text = text.replace('هر', 'every')
    text = text.replace('روز', 'day')

    # Period usage: سال => year, ماه => month, هفته => week, etc.
    text = text.replace('سال', 'year')
    text = text.replace('ماه', 'month')
    text = text.replace('هفته', 'week')

    return text

def parse_investment_period(period_str: str) -> timedelta:
    """
    Parses a human-readable period string into a timedelta.
    e.g.: "1 year", "2 months", "3 weeks", "1 day" (in English or Farsi).
    Defaults to 1 year if unrecognized.
    """
    period_str = persian_to_ascii(period_str.lower().strip())
    tokens = period_str.split()

    quantity = 1
    for token in tokens:
        if token.isdigit():
            quantity = int(token)
            break

    if "year" in period_str:
        return timedelta(days=365 * quantity)
    elif "month" in period_str:
        return timedelta(days=30 * quantity)
    elif "week" in period_str:
        return timedelta(days=7 * quantity)
    elif "day" in period_str:
        return timedelta(days=1 * quantity)
    else:
        # default 1 year
        return timedelta(days=365)

def parse_investment_frequency(freq_str: str):
    """
    Parse frequency string in both English & Farsi (digit conversion + basic word mapping),
    returning (frequency_value, is_hourly).

    Examples:
      - "weekly", "هفتگی" => (7, False)
      - "biweekly", "هر دو هفته" => (14, False)
      - "monthly", "ماهانه" => (30, False)
      - "daily", "روزانه" => (1, False)
      - "every 3 days", "هر ۳ روز" => (3, False)
      - "hourly", "ساعتی" => (1, True)
      - "every 2 hours", "هر ۲ ساعت" => (2, True)

    If unknown, default to (7, False) meaning 7 days (weekly).
    """
    freq_str = freq_str.lower().replace("-", "")
    freq_str = persian_to_ascii(freq_str)

    # If user typed something about hour => is_hourly = True
    if "hour" in freq_str:
        # e.g. "every 2 hour", "2 hour", "hourly"
        parts = freq_str.split()
        interval_val = 1
        for p in parts:
            if p.isdigit():
                interval_val = int(p)
                break
        return (interval_val, True)

    # else interpret as daily approach
    # check if "biweekly" => 14 days
    if "biweek" in freq_str:
        return (14, False)
    elif "week" in freq_str:
        return (7, False)
    elif "month" in freq_str:
        return (30, False)
    elif "daily" in freq_str or "day" in freq_str:
        return (1, False)
    else:
        # default => weekly
        return (7, False)

def calculate_dca(
    total_investment: float,
    symbol: str,
    start_dt: datetime,
    end_dt: datetime,
    freq_value: int,
    is_hourly: bool,
    fee_percent: float = 0.0
):
    """
    If is_hourly = True => fetch "1h" klines, iterate every freq_value hours
    Else => fetch "1d" klines, iterate every freq_value days
    """
    # Decide the binance interval
    kline_interval = "1h" if is_hourly else "1d"

    # Fetch closing prices with that interval
    closing_prices = get_closing_prices(symbol, start_dt, end_dt, interval=kline_interval)
    if not closing_prices:
        raise ValueError("No historical price data found for the given period.")

    investment_points = []
    if is_hourly:
        # Build hourly points
        current_dt = start_dt
        while current_dt <= end_dt:
            # key format might be "YYYY-MM-DD HH"
            dt_str = current_dt.strftime("%Y-%m-%d %H")
            if dt_str in closing_prices:
                investment_points.append(dt_str)
            current_dt += timedelta(hours=freq_value)
    else:
        # daily approach => keys like "YYYY-MM-DD"
        current_date = start_dt.date()
        while current_date <= end_dt.date():
            dt_str = current_date.strftime("%Y-%m-%d")
            if dt_str in closing_prices:
                investment_points.append(dt_str)
            current_date += timedelta(days=freq_value)

    if not investment_points:
        raise ValueError("No valid investment points found in the data range.")

    number_of_investments = len(investment_points)
    amount_per_investment = total_investment / number_of_investments

    total_coins_purchased = 0.0
    purchase_history = []

    for point in investment_points:
        price = closing_prices[point]
        net_invest = amount_per_investment * (1 - fee_percent / 100.0)
        coins = net_invest / price
        total_coins_purchased += coins
        purchase_history.append((point, price, coins))

    avg_purchase_price = total_investment / total_coins_purchased
    current_price = fetch_current_price(symbol)
    current_portfolio_value = current_price * total_coins_purchased
    roi_percent = ((current_portfolio_value / total_investment) - 1) * 100

    # Lump-sum => buy everything at the first point's price
    first_point = investment_points[0]
    lump_sum_price = closing_prices[first_point]
    net_ls = total_investment * (1 - fee_percent/100.0)
    lump_sum_coins = net_ls / lump_sum_price
    lump_sum_value = lump_sum_coins * current_price
    lump_sum_roi = ((lump_sum_value / total_investment) - 1) * 100

    # (Optional) annualized calculations if you want
    return {
        "symbol": symbol,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "freq_value": freq_value,
        "is_hourly": is_hourly,
        "fee_percent": fee_percent,
        "total_investment": total_investment,
        "number_of_investments": number_of_investments,
        "purchase_history": purchase_history,
        "total_coins_purchased": total_coins_purchased,
        "avg_purchase_price": avg_purchase_price,
        "current_price": current_price,
        "current_portfolio_value": current_portfolio_value,
        "roi_percent": roi_percent,
        "lump_sum_roi": lump_sum_roi
    }
