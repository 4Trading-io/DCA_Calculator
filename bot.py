# bot.py

import os
import logging
from telebot import TeleBot, types
from credentials import telegram_bot_tokens
from data_store import DataStore
from commands import register_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


TELEGRAM_BOT_TOKEN = telegram_bot_tokens

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set. Please check your .env file.")

def main():
    # 1) Create bot instance
    bot = TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="Markdown")
    store = DataStore()

    # 2) Register conversation handlers
    register_handlers(bot, store)

    # 3) *Set your custom commands menu* (the "blue button")
    bot.set_my_commands([
        types.BotCommand("start", "شروع گفت‌وگو / Start the DCA calculation flow"),
        types.BotCommand("help", "راهنما / Show help"),
        types.BotCommand("language", "تغییر زبان / Change language"),
        types.BotCommand("cancel", "لغو فرایند / Cancel current process"),
        types.BotCommand("restart", "ریست / Restart the entire flow"),
    ])

    # 4) Start polling
    logger.info("Bot is running... Press Ctrl+C to stop.")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
