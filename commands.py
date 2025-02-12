# commands.py

import logging
from datetime import datetime, timedelta

from telebot import TeleBot, types
from data_store import DataStore, BotState
from dca_calculator import (
    parse_investment_period,
    parse_investment_frequency,
    calculate_dca
)
from chart import create_dca_plot
from localization import tr

logger = logging.getLogger(__name__)

def register_handlers(bot: TeleBot, store: DataStore):
    """Attach command and message handlers to the bot."""

    def language_inline_keyboard():
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton(tr("language_choice_en"), callback_data="lang_en"),
            types.InlineKeyboardButton(tr("language_choice_es"), callback_data="lang_fa")
        )
        return kb

    def settings_keyboard(lang='en'):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("Settings"))
        return kb

    def parse_date_or_relative(text: str):
        """
        Accepts YYYY-MM-DD or phrases like '1 year ago', '6 months ago', 'today'.
        Returns a datetime or raises ValueError.
        """
        text = text.strip().lower()
        now = datetime.utcnow()

        if text == "today":
            return now

        if "ago" in text:
            tokens = text.split()
            if len(tokens) < 3:
                raise ValueError("Invalid relative expression.")
            try:
                quantity = int(tokens[0])
            except ValueError:
                raise ValueError("Invalid number in relative date.")

            unit = tokens[1]
            if "year" in unit:
                return now - timedelta(days=365 * quantity)
            elif "month" in unit:
                return now - timedelta(days=30 * quantity)
            elif "week" in unit:
                return now - timedelta(days=7 * quantity)
            elif "day" in unit:
                return now - timedelta(days=1 * quantity)
            else:
                raise ValueError("Unknown unit in relative date.")
        else:
            # Attempt exact date
            try:
                dt = datetime.strptime(text, "%Y-%m-%d")
                return dt
            except ValueError:
                pass

        raise ValueError("Invalid date format. Please use YYYY-MM-DD or 'X months ago', etc.")

    @bot.message_handler(commands=["start"])
    def command_start(message):
        user_id = message.chat.id
        session = store.reset_session(user_id)
        session.state = BotState.LANG_SELECT

        bot.send_message(
            user_id,
            tr("start_multi_lang_msg", 'en'),
            reply_markup=language_inline_keyboard(),
            parse_mode="Markdown"
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
    def callback_language(call):
        user_id = call.message.chat.id
        session = store.get_session(user_id)

        if call.data == "lang_en":
            session.lang = 'en'
            bot.answer_callback_query(call.id, tr("language_set", 'en'))
        elif call.data == "lang_fa":
            session.lang = 'fa'
            bot.answer_callback_query(call.id, tr("language_set_es", 'fa'))

        bot.send_message(
            user_id,
            tr("welcome_dca_explanation", session.lang),
            parse_mode="Markdown"
        )

        session.state = BotState.ENTERING_AMOUNT
        bot.send_message(
            user_id,
            tr("ask_amount", session.lang),
            reply_markup=settings_keyboard(session.lang),
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["help"])
    def command_help(message):
        user_id = message.chat.id
        session = store.get_session(user_id)
        bot.send_message(
            user_id,
            tr("help_message", session.lang),
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["cancel"])
    def command_cancel(message):
        user_id = message.chat.id
        session = store.get_session(user_id)
        session.state = BotState.IDLE
        bot.send_message(
            user_id,
            tr("cancel_message", session.lang),
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["restart"])
    def command_restart(message):
        user_id = message.chat.id
        store.reset_session(user_id)
        bot.send_message(user_id, tr("restart_message", 'en'), parse_mode="Markdown")
        
    @bot.message_handler(commands=["language"])
    def command_language(message):
        user_id = message.chat.id
        session = store.get_session(user_id)

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tr("choose_lang_button", session.lang), callback_data="show_lang"))
        bot.send_message(
            user_id,
            tr("settings_menu", session.lang),
            reply_markup=kb,
            parse_mode="Markdown"
        )

    @bot.message_handler(func=lambda m: m.text == "Settings")
    def command_settings(message):
        user_id = message.chat.id
        session = store.get_session(user_id)

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(tr("choose_lang_button", session.lang), callback_data="show_lang"))
        bot.send_message(
            user_id,
            tr("settings_menu", session.lang),
            reply_markup=kb,
            parse_mode="Markdown"
        )

    @bot.callback_query_handler(func=lambda call: call.data == "show_lang")
    def callback_show_lang(call):
        user_id = call.message.chat.id
        session = store.get_session(user_id)
        bot.answer_callback_query(call.id, "")
        bot.send_message(
            user_id,
            tr("lang_prompt", session.lang),
            reply_markup=language_inline_keyboard(),
            parse_mode="Markdown"
        )

    # -------- MAIN FLOW --------
    @bot.message_handler(func=lambda m: True)
    def conversation_flow(message):
        user_id = message.chat.id
        session = store.get_session(user_id)
        text = message.text.strip()

        if session.state == BotState.IDLE:
            bot.send_message(
                user_id,
                tr("not_sure", session.lang),
                parse_mode="Markdown"
            )
            return

        if session.state == BotState.LANG_SELECT:
            bot.send_message(
                user_id,
                tr("lang_prompt", session.lang),
                reply_markup=language_inline_keyboard(),
                parse_mode="Markdown"
            )
            return

        if session.state == BotState.ENTERING_AMOUNT:
            handle_investment_amount(bot, store, message)
        elif session.state == BotState.ENTERING_SYMBOL:
            handle_symbol(bot, store, message)
        elif session.state == BotState.ASK_DATE_RANGE_OR_PERIOD:
            handle_ask_date_range_or_period(bot, store, message)
        elif session.state == BotState.ASK_CUSTOM_BOTH_RANGE:
            handle_ask_both_range(bot, store, message)
        elif session.state == BotState.ENTERING_RANGE_START:
            handle_range_start(bot, store, message, parse_date_or_relative)
        elif session.state == BotState.ENTERING_RANGE_END:
            handle_range_end(bot, store, message, parse_date_or_relative)
        elif session.state == BotState.ENTERING_PERIOD:
            handle_period(bot, store, message)
        elif session.state == BotState.ASK_CUSTOM_START:
            handle_ask_custom_start(bot, store, message)
        elif session.state == BotState.ENTERING_CUSTOM_START:
            handle_custom_start(bot, store, message)
        elif session.state == BotState.ENTERING_FREQUENCY:
            handle_frequency(bot, store, message)
        elif session.state == BotState.ENTERING_FEE:
            handle_fee(bot, store, message)
        elif session.state == BotState.CALCULATE:
            perform_calculation(bot, store, message)
        else:
            bot.send_message(
                user_id,
                tr("not_sure", session.lang),
                parse_mode="Markdown"
            )

# ---- Step Handlers ----
def handle_investment_amount(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.strip().replace("$", "")

    try:
        amount = float(text)
        session.total_investment = amount
        session.state = BotState.ENTERING_SYMBOL
        bot.send_message(
            user_id,
            tr("ask_symbol", session.lang),
            parse_mode="Markdown"
        )
    except ValueError:
        bot.send_message(
            user_id,
            tr("invalid_amount", session.lang),
            parse_mode="Markdown"
        )

def handle_symbol(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    pair_str = message.text.upper().replace("/", "").strip()
    session.symbol = pair_str

    session.state = BotState.ASK_DATE_RANGE_OR_PERIOD
    bot.send_message(
        user_id,
        tr("ask_range_or_period", session.lang),
        parse_mode="Markdown"
    )

def handle_ask_date_range_or_period(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.lower()

    if "range" in text:
        session.state = BotState.ASK_CUSTOM_BOTH_RANGE
        bot.send_message(
            user_id,
            tr("ask_range_continue", session.lang),
            parse_mode="Markdown"
        )
    elif "period" in text:
        session.state = BotState.ENTERING_PERIOD
        bot.send_message(
            user_id,
            tr("ask_period", session.lang),
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            user_id,
            tr("ask_range_or_period", session.lang),
            parse_mode="Markdown"
        )

def handle_ask_both_range(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    session.state = BotState.ENTERING_RANGE_START

    bot.send_message(
        user_id,
        tr("ask_range_start_instructions", session.lang),
        parse_mode="Markdown"
    )

def handle_range_start(bot, store, message, parse_func):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.strip()

    try:
        start_dt = parse_func(text)
        session.custom_start_date = start_dt
        session.state = BotState.ENTERING_RANGE_END

        bot.send_message(
            user_id,
            tr("ask_range_end_instructions", session.lang),
            parse_mode="Markdown"
        )
    except ValueError as e:
        bot.send_message(
            user_id,
            tr("range_parse_error_start", session.lang).format(error=str(e)),
            parse_mode="Markdown"
        )

def handle_range_end(bot, store, message, parse_func):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.strip()

    try:
        end_dt = parse_func(text)
        session.custom_range_end_date = end_dt
        session.state = BotState.ENTERING_FREQUENCY

        bot.send_message(
            user_id,
            tr("ask_frequency", session.lang),
            parse_mode="Markdown"
        )
    except ValueError as e:
        bot.send_message(
            user_id,
            tr("range_parse_error_end", session.lang).format(error=str(e)),
            parse_mode="Markdown"
        )

def handle_period(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    session.period_str = message.text.strip()

    session.state = BotState.ASK_CUSTOM_START
    bot.send_message(
        user_id,
        tr("ask_custom_start", session.lang),
        parse_mode="Markdown"
    )

def handle_ask_custom_start(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.lower()

    if text in ["yes", "y", "بله", "bale"]:
        session.state = BotState.ENTERING_CUSTOM_START
        bot.send_message(
            user_id,
            tr("ask_enter_custom_start", session.lang),
            parse_mode="Markdown"
        )
    else:
        session.custom_start_date = None
        session.state = BotState.ENTERING_FREQUENCY
        bot.send_message(
            user_id,
            tr("ask_frequency", session.lang),
            parse_mode="Markdown"
        )

def handle_custom_start(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.strip()

    try:
        dt = datetime.strptime(text, "%Y-%m-%d")
        session.custom_start_date = dt
        session.state = BotState.ENTERING_FREQUENCY
        bot.send_message(
            user_id,
            tr("ask_frequency", session.lang),
            parse_mode="Markdown"
        )
    except ValueError:
        bot.send_message(
            user_id,
            tr("invalid_date", session.lang),
            parse_mode="Markdown"
        )

def handle_frequency(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    freq_str = message.text.strip()
    # parse freq => daily or hourly
    (freq_value, is_hourly) = parse_investment_frequency(freq_str)

    session.freq_value = freq_value
    session.freq_is_hourly = is_hourly

    session.state = BotState.ENTERING_FEE
    bot.send_message(
        user_id,
        tr("ask_fee", session.lang),
        parse_mode="Markdown"
    )

def handle_fee(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    text = message.text.strip().replace("%", "")

    try:
        fee = float(text)
        if fee < 0:
            raise ValueError("Fee cannot be negative.")
        session.fee_percent = fee

        session.state = BotState.CALCULATE
        perform_calculation(bot, store, message)
    except ValueError:
        bot.send_message(
            user_id,
            tr("invalid_fee", session.lang),
            parse_mode="Markdown"
        )

def perform_calculation(bot, store, message):
    user_id = message.chat.id
    session = store.get_session(user_id)
    lang = session.lang

    bot.send_message(
        user_id,
        tr("calculating", lang),
        parse_mode="Markdown"
    )

    try:
        total_investment = session.total_investment
        symbol = session.symbol
        freq_value = session.freq_value
        is_hourly = session.freq_is_hourly
        fee_percent = session.fee_percent

        if session.custom_range_end_date:
            start_dt = session.custom_start_date
            end_dt = session.custom_range_end_date
        else:
            # period approach
            end_dt = datetime.utcnow()
            if session.custom_start_date:
                start_dt = session.custom_start_date
            else:
                delta = parse_investment_period(session.period_str)
                start_dt = end_dt - delta

        if start_dt > end_dt:
            raise ValueError("Start date is after end date. Please ensure start <= end.")

        # Now call calculate_dca with the new approach
        dca_result = calculate_dca(
            total_investment=total_investment,
            symbol=symbol,
            start_dt=start_dt,
            end_dt=end_dt,
            freq_value=freq_value,
            is_hourly=is_hourly,
            fee_percent=fee_percent
        )

        chart_path = create_dca_plot(dca_result["purchase_history"], symbol)

        report_text = build_report_caption(dca_result, lang)
        # Truncate if caption is too long
        if len(report_text) > 1000:
            report_text = report_text[:1000] + "\n... (truncated)"

        with open(chart_path, "rb") as photo:
            bot.send_photo(
                user_id,
                photo,
                caption=report_text,
                parse_mode="Markdown"
            )

        session.state = BotState.IDLE

    except ValueError as e:
        logger.error(f"ValueError: {e}")
        bot.send_message(
            user_id,
            tr("error_value", lang) + str(e),
            parse_mode="Markdown"
        )
        session.state = BotState.IDLE
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        bot.send_message(
            user_id,
            tr("error_unexpected", lang) + str(e),
            parse_mode="Markdown"
        )
        session.state = BotState.IDLE

def build_report_caption(dca_result, lang):
    """
    We keep the old approach for final text.
    You could add your own annualized logic, etc.
    """
    symbol = dca_result["symbol"]
    total_inv = dca_result["total_investment"]
    total_coins = dca_result["total_coins_purchased"]
    avg_price = dca_result["avg_purchase_price"]
    curr_price = dca_result["current_price"]
    curr_value = dca_result["current_portfolio_value"]
    roi = dca_result["roi_percent"]
    ls_roi = dca_result["lump_sum_roi"]

    if lang == 'fa':
        caption = (
            f"✅ *گزارش نهایی DCA شما*\n\n"
            f"🔸 **جفت ارز:** {symbol}\n"
            f"💰 **مبلغ کل سرمایه‌گذاری:** {total_inv:,.2f}$\n"
            f"🔹 **تعداد کوین خریداری‌شده:** {total_coins:.6f}\n"
            f"⚖️ **میانگین قیمت خرید:** {avg_price:,.2f}$\n"
            f"🔎 **قیمت فعلی:** {curr_price:,.2f}$\n"
            f"💼 **ارزش فعلی پرتفوی:** {curr_value:,.2f}$\n"
            f"📈 **درصد بازدهی (ROI):** {roi:+.2f}%\n\n"
            f"💥 **مقایسه با خرید یکجا:**\n"
            f"• بازدهی کلی: {ls_roi:+.2f}%\n\n"
            f"_DCA می‌تواند ریسک زمان‌بندی بازار را کم کند (مشاورهٔ مالی نیست)_"
        )
    else:
        caption = (
            f"✅ *Your Final DCA Report*\n\n"
            f"🔸 **Pair:** {symbol}\n"
            f"💰 **Total Investment:** ${total_inv:,.2f}\n"
            f"🔹 **Coins Purchased:** {total_coins:.6f}\n"
            f"⚖️ **Average Cost:** ${avg_price:,.2f}\n"
            f"🔎 **Current Price:** ${curr_price:,.2f}\n"
            f"💼 **Current Portfolio Value:** ${curr_value:,.2f}\n"
            f"📈 **ROI:** {roi:+.2f}%\n\n"
            f"💥 **Lump-Sum Comparison:**\n"
            f"• Overall ROI: {ls_roi:+.2f}%\n\n"
            f"_DCA helps reduce market-timing risk (Not financial advice)_"
        )
    return caption
