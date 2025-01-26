# dca_calculator.py

import math
import logging
from datetime import datetime, timedelta

from binance_api import get_daily_closing_prices, fetch_current_price

logger = logging.getLogger(__name__)

def persian_to_ascii(text: str) -> str:
    """
    Convert Persian digits to ASCII digits,
    and also do some replacements to help parse time units in Farsi.
    """
    # Map Persian digits to ASCII
    digits_map = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    for p_digit, en_digit in digits_map.items():
        text = text.replace(p_digit, en_digit)

    # Some optional replacements to unify Farsi words
    # We'll convert them to rough English placeholders for easier logic
    text = text.replace('هفتگی', 'weekly')
    text = text.replace('هر دو هفته', 'biweekly')
    text = text.replace('ماهانه', 'monthly')
    text = text.replace('ماهیانه', 'monthly')  # in case user uses "ماهیانه"
    text = text.replace('روزانه', 'daily')

    # "هر X روز"
    # We won't replace blindly, but if user typed "هر 3 روز"
    # We'll unify "هر" to "every" so parse can see "every 3 day"
    text = text.replace('هر', 'every')
    text = text.replace('روز', 'day')  # This might help "every 3 day"

    # For period usage: replace 'سال' => 'year', 'ماه' => 'month', etc. too
    text = text.replace('سال', 'year')
    text = text.replace('ماه', 'month')
    text = text.replace('هفته', 'week')

    return text


def parse_investment_period(period_str: str) -> timedelta:
    """
    Parses a human-readable period string into a timedelta.
    Supports day/week/month/year in BOTH English & Farsi.
    If unrecognized, defaults to 1 year.
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
        # Default 1 year if uncertain
        return timedelta(days=365)

def parse_investment_frequency(freq_str: str) -> int:
    """
    Parse frequency string in both English & Farsi (digit conversion + basic word mapping),
    and return days between purchases.

    Examples that should now work:
      - "weekly" or "هفتگی" -> 7
      - "bi-weekly" or "biweekly" or "هر دو هفته" -> 14
      - "monthly" or "ماهانه" -> 30
      - "daily" or "روزانه" -> 1
      - "every 3 days" or "هر ۳ روز" -> 3

    Defaults to 7 if unrecognized.
    """
    freq_str = freq_str.lower().replace("-", "")
    freq_str = persian_to_ascii(freq_str)  # Convert Persian digits & words

    # Check "every X day"
    if freq_str.startswith("every") and "day" in freq_str:
        tokens = freq_str.split()
        for t in tokens:
            if t.isdigit():
                return int(t)

    if "biweekly" in freq_str or "biweek" in freq_str:
        return 14
    elif "weekly" in freq_str:
        return 7
    elif "monthly" in freq_str:
        return 30
    elif "daily" in freq_str:
        return 1

    # If we see "day" alone
    elif "day" in freq_str:
        return 1
    else:
        return 7  # default weekly

def calculate_dca(
    total_investment: float,
    symbol: str,
    start_dt: datetime,
    end_dt: datetime,
    frequency_days: int,
    fee_percent: float = 0.0
):
    """
    Perform DCA calculation:
      - Split total investment into equal parts at each interval.
      - Fetch historical daily prices.
      - Deduct fee if provided.
      - Return dictionary of DCA stats, lumpsum stats, etc.
    """
    daily_prices = get_daily_closing_prices(symbol, start_dt, end_dt)
    if not daily_prices:
        raise ValueError("No historical price data found for the given period.")

    investment_dates = []
    current_date = start_dt.date()
    while current_date <= end_dt.date():
        date_str = str(current_date)
        if date_str in daily_prices:
            investment_dates.append(current_date)
        current_date += timedelta(days=frequency_days)

    if not investment_dates:
        raise ValueError("No valid investment dates found in the data range.")

    number_of_investments = len(investment_dates)
    amount_per_investment = total_investment / number_of_investments

    total_coins_purchased = 0.0
    purchase_history = []

    for date_ in investment_dates:
        date_str = str(date_)
        price = daily_prices[date_str]
        net_investment = amount_per_investment * (1 - (fee_percent / 100.0))
        coins = net_investment / price
        total_coins_purchased += coins
        purchase_history.append((date_str, price, coins))

    avg_purchase_price = total_investment / total_coins_purchased
    current_price = fetch_current_price(symbol)
    current_portfolio_value = current_price * total_coins_purchased
    roi_percent = ((current_portfolio_value / total_investment) - 1) * 100

    # Lump-sum calculation
    first_date_str = str(investment_dates[0])
    lump_sum_price = daily_prices[first_date_str]
    net_investment_ls = total_investment * (1 - (fee_percent / 100.0))
    lump_sum_coins = net_investment_ls / lump_sum_price
    lump_sum_current_value = current_price * lump_sum_coins
    lump_sum_roi = ((lump_sum_current_value / total_investment) - 1) * 100

    total_days = (end_dt.date() - investment_dates[0]).days
    if total_days < 1:
        annualized_dca = roi_percent
        annualized_lump_sum = lump_sum_roi
    else:
        dca_growth_factor = current_portfolio_value / total_investment
        annualized_dca = (dca_growth_factor ** (365.0 / total_days) - 1) * 100

        lump_sum_growth_factor = lump_sum_current_value / total_investment
        annualized_lump_sum = (lump_sum_growth_factor ** (365.0 / total_days) - 1) * 100

    return {
        "symbol": symbol,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "frequency_days": frequency_days,
        "fee_percent": fee_percent,
        "total_investment": total_investment,
        "number_of_investments": number_of_investments,
        "purchase_history": purchase_history,
        "total_coins_purchased": total_coins_purchased,
        "avg_purchase_price": avg_purchase_price,
        "current_price": current_price,
        "current_portfolio_value": current_portfolio_value,
        "roi_percent": roi_percent,
        "lump_sum_roi": lump_sum_roi,
        "annualized_dca": annualized_dca,
        "annualized_lump_sum": annualized_lump_sum,
    }
