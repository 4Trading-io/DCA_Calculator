# bot.py

import os
import logging
from telebot import TeleBot
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
    bot = TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="Markdown")
    store = DataStore()

    register_handlers(bot, store)

    logger.info("Bot is running... Press Ctrl+C to stop.")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
