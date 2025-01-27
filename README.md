# DCA Telegram Bot (English/Farsi)

A **Telegram Bot** that demonstrates how Dollar-Cost Averaging (DCA) can perform over a given time period, supporting both **English** and **Farsi** (Persian) languages. Users can specify:

- **Total investment** (USD)  
- **Crypto pair** (e.g., BTC/USDT)  
- **Investment period** or **custom date range**  
- **Investment frequency** (weekly, monthly, هفتگی، ماهانه, etc.)  
- **Optional trading fee**  

The bot then compares the **DCA** approach to a **lump-sum** buy, calculates your final portfolio value, ROI, and **annualized** ROI, and returns a **plot** of purchase prices over time.


## Table of Contents

1. [Features](#features)  
2. [Screenshots](#screenshots)  
3. [Architecture & Files](#architecture--files)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Environment Variables](#environment-variables)  
7. [Languages & Localization](#languages--localization)  
8. [Technical Notes](#technical-notes)  
9. [Contributing](#contributing)  
10. [License](#license)

## Features

1. **Dual Language Support** – Offers both English and Farsi. The user chooses a language at startup or changes it later via the **Settings** menu.
2. **DCA vs. Lump-Sum** – Compares hypothetical DCA results with a one-time purchase, showing ROI and annualized returns.
3. **Period or Full Date Range** – User can specify a relative period (e.g., "6 months"), or choose an exact date range (e.g., "1 year ago" to "6 months ago" or specific `YYYY-MM-DD`).
4. **Chart Generation** – Visualizes purchase prices over time using Matplotlib and sends the chart as an image in Telegram.
5. **Persian Digit Handling** – The bot parses both English and Persian numeric inputs, plus words like “هفتگی,” “هر دو هفته,” etc.
6. **Settings Menu** – Inline buttons for quickly changing language or restarting.


**Key modules**:

- **`commands.py`** – Contains all Telegram conversation handlers (step-by-step flow, messages).
- **`localization.py`** – Stores and retrieves strings in both English and Farsi.
- **`dca_calculator.py`** – Core logic for DCA calculations, ROI, annualized returns.
- **`binance_api.py`** – Fetches daily/weekly/monthly price data and current ticker prices from Binance.
- **`chart.py`** – Generates a PNG plot with Matplotlib.


## 7. **Usage**

## Usage

- In **Telegram**, find your bot (e.g., `t.me/<YourBotUsername>`) and type `/start`.  
- You’ll see a **bilingual** greeting, then choose **English** or **Farsi**.  
- Follow the steps:
  1. **Enter total USD investment** (e.g., 1000).  
  2. **Crypto pair** (e.g., BTC/USDT).  
  3. Choose either:
     - **Exact Date Range** (e.g., "1 year ago" to "6 months ago," or `2022-01-01` to `2022-06-01`).
     - **Period** (e.g., "1 year" plus an optional custom start date).
  4. **Frequency** (“weekly,” “bi-weekly,” “monthly,” “هفتگی,” etc.).  
  5. **Fee** (optional).  
- The bot calculates your DCA results vs. lump-sum, then sends a chart with the final report.


## Environment Variables

- **`TELEGRAM_BOT_TOKEN`** – Your unique Telegram bot token (required).
- *(If you plan to add more environment variables, list them here.)*

## Languages & Localization

- **English** and **Farsi** are supported out of the box.
- Users can switch languages at any time using the **Settings** button or by restarting the bot.
- The `localization.py` file can be extended to add more languages if needed.


## Technical Notes

1. **Binance Public API** – Fetches historical candlestick (kline) data at `https://api.binance.com/api/v3/klines` and current prices (`/api/v3/ticker/price`).
2. **Caching** – In-memory caching of fetched data to reduce redundant calls.
3. **Matplotlib** – Runs headless (`Agg` backend) to generate PNG charts.
4. **Session Management** – Uses `DataStore` to keep conversation states in memory. Not persistent across restarts.
5. **Persian Digit Handling** – `dca_calculator.py` uses `persian_to_ascii()` to convert Persian digits/words into a unified format for calculating.

## Contributing

Contributions are welcome! To get started:

1. **Fork** the repository on GitHub.
2. Create a **feature branch**.
3. **Commit** your changes.
4. **Push** your branch.
5. Open a **Pull Request** describing your additions or changes.

Please include relevant **tests** (if applicable) and documentation updates for new features or bug fixes.


## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.


