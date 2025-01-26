# localization.py

def tr(key: str, lang: str = 'en') -> str:
    """
    برگرداندن متن ترجمه شده برای کلید داده‌شده در زبان مربوطه.
    اگر کلید در زبان خواسته‌شده موجود نباشد، متن زبان انگلیسی برگردانده می‌شود.
    """
    return MESSAGES[lang].get(key, MESSAGES['en'].get(key, key))

MESSAGES = {
    'en': {
        "start_multi_lang_msg": (
            "Hello! / سلام!\n\n"
            "Please choose a language below to continue.\n"
            "لطفاً زبان خود را برای ادامه انتخاب کنید."
        ),
        "welcome_dca_explanation": (
            "🤖 *Welcome to the DCA Calculator Bot!*\n\n"
            "Dollar-Cost Averaging (DCA) is an investment strategy where you invest "
            "a fixed amount at regular intervals, regardless of the asset price. "
            "This helps avoid \"timing the market\" and can reduce volatility impact.\n\n"
            "*How this bot works:*\n"
            "• We'll ask for your total investment\n"
            "• Your crypto pair\n"
            "• The time period or exact date range\n"
            "• How often you invest\n"
            "Then we'll compare your DCA returns vs. a lump-sum buy.\n\n"
            "Use the buttons below to select language or type /help. You can always "
            "change language later in the Settings menu.\n\n"
            "*Ready to begin?* 🚀"
        ),
        "lang_prompt": "🗣 *Please choose a language:*",
        "language_set": "✅ Language set to English!",
        "language_set_es": "✅ Language set to Farsi!",
        "help_message": (
            "ℹ️ *DCA Calculator Bot Help*\n\n"
            "• /start – Begin a new DCA calculation\n"
            "• /help – Show this help\n"
            "• /cancel – Cancel current process\n"
            "• /restart – Restart the flow\n\n"
            "*Disclaimer:* Educational tool only, not financial advice!"
        ),
        "cancel_message": "✅ Process canceled. Type /start to begin again.",
        "restart_message": "🔄 Session restarted. Type /start to begin fresh!",
        "not_sure": "I didn't understand that. Try /start or use the menu below.",
        "ask_amount": (
            "💰 *Step 1:* How much money (USD) do you want to invest *in total*?\n\n"
            "_Example:_ 1000 or 1200.50"
        ),
        "invalid_amount": "❌ Please enter a valid amount (e.g., 1000 or 1200.50).",
        "ask_symbol": (
            "💱 *Step 2:* Which *crypto pair* would you like to invest in?\n\n"
            "_Example:_ BTC/USDT, ETH/USDT, etc."
        ),
        # ------ Range or Period ------
        "ask_range_or_period": (
            "Would you like to specify an *exact custom date range (start & end)*,\n"
            "or use the *traditional period method*?\n\n"
            "Type 'range' to specify start/end dates (exact or relative like '1 year ago', '6 months ago').\n"
            "Type 'period' to proceed with the older approach (e.g. '1 year' plus optional custom start).\n\n"
            "Example usage:\n"
            "- 'range'\n"
            "- 'period'"
        ),
        "ask_range_continue": (
            "Great! We'll collect *start date* and *end date* next.\n\n"
            "Type anything to continue..."
        ),
        "ask_range_start_instructions": (
            "📅 *Custom Date Range (Start)*\n\n"
            "Please provide your *start date*. You can use:\n"
            "- An exact date, e.g. `2022-01-01`\n"
            "- A relative expression, e.g. `1 year ago`, `6 months ago`, `today`\n\n"
            "Examples:\n"
            "`2023-01-01`\n"
            "`1 year ago`\n\n"
            "Type your start date now:"
        ),
        "ask_range_end_instructions": (
            "📅 *Custom Date Range (End)*\n\n"
            "Now provide your *end date*. You can also use:\n"
            "- Exact date, e.g. `2023-01-01`\n"
            "- Relative expression, e.g. `6 months ago`, `today`\n\n"
            "Examples:\n"
            "`2023-06-01`\n"
            "`6 months ago`\n"
            "`today`\n\n"
            "Type your end date now:"
        ),
        # ------ Range parse errors ------
        "range_parse_error_start": "❌ {error}\nTry again. Example: `2022-01-01` or `6 months ago`",
        "range_parse_error_end": "❌ {error}\nTry again. Example: `2023-01-01` or `2 weeks ago` or `today`",

        "ask_period": (
            "⏱ *Step 3:* Over what period do you want to invest?\n\n"
            "_Examples:_ 1 year, 6 months, 2 weeks."
        ),
        "ask_custom_start": (
            "📅 Do you want to specify a *custom start date*?\n\n"
            "If not, we'll assume the period ends *today* and go backward.\n"
            "Type `yes` or `no`."
        ),
        "ask_enter_custom_start": (
            "✏️ Please enter your start date in `YYYY-MM-DD`.\n\n"
            "_Example:_ 2022-01-01"
        ),
        "invalid_date": "❌ Invalid date format. Please use YYYY-MM-DD.",
        "ask_frequency": (
            "🔁 *Step 4:* How often will you invest?\n\n"
            "_Examples:_ weekly, bi-weekly, monthly, every 3 days."
        ),
        "ask_fee": (
            "💸 *Step 5:* Enter the *trading fee percentage* (if any).\n\n"
            "_Example:_ `0.1` means 0.1% fee. Enter 0 if none."
        ),
        "invalid_fee": "❌ Invalid fee. Must be a non-negative number (e.g. 0.1).",
        "calculating": "⌛ *Calculating your DCA performance...* Please wait...",
        "final_prompt": "✅ Done! Here's your DCA report:",
        "error_value": "❌ Error: ",
        "error_unexpected": "❌ Unexpected error: ",
        "settings_menu": "⚙️ *Settings:* Choose an option below.",
        "set_language_button": "Change Language",
        "back_button": "« Back",
        "choose_lang_button": "Choose Language",
        "language_choice_en": "English",
        "language_choice_es": "Farsi",
    },

    'fa': {
        "start_multi_lang_msg": (
            "سلام! / Hello!\n\n"
            "برای ادامه یکی از زبان‌های زیر را انتخاب کنید.\n"
            "Please choose your preferred language to continue."
        ),
        "welcome_dca_explanation": (
            "🤖 *به ربات محاسبهٔ DCA خوش آمدید!*\n\n"
            "«میانگین هزینهٔ دلاری» (DCA) روشی است که در آن شما به‌طور منظم "
            "و در فواصل زمانی مشخص مبلغ ثابتی را سرمایه‌گذاری می‌کنید، "
            "صرف‌نظر از قیمت فعلی دارایی. این کار به شما کمک می‌کند که "
            "از «زمان‌بندی بازار» بپرهیزید و ریسک نوسانات را کاهش دهید.\n\n"
            "*این ربات چگونه کار می‌کند:*\n"
            "• مبلغ کل سرمایه‌گذاری شما\n"
            "• جفت رمز ارزی که می‌خواهید بخرید\n"
            "• مدت زمان یا بازهٔ تاریخی دقیق سرمایه‌گذاری\n"
            "• تناوب خریدهای شما\n"
            "در نهایت بازدهی روش DCA را با خرید یکجای دارایی مقایسه می‌کنیم.\n\n"
            "از دکمه‌های زیر برای انتخاب زبان استفاده کنید یا دستور /help را وارد کنید. "
            "همچنین می‌توانید با دکمهٔ «Settings» در آینده زبان را تغییر دهید.\n\n"
            "*آماده‌اید شروع کنیم؟* 🚀"
        ),
        "lang_prompt": "🗣 *لطفاً زبان مورد نظر را انتخاب کنید:*",
        "language_set": "✅ زبان به انگلیسی تغییر یافت!",
        "language_set_es": "✅ زبان به فارسی تغییر یافت!",
        "help_message": (
            "ℹ️ *راهنمای ربات محاسبهٔ DCA*\n\n"
            "• /start – آغاز یک محاسبهٔ جدید DCA\n"
            "• /help – نمایش این راهنما\n"
            "• /cancel – لغو فرایند جاری\n"
            "• /restart – شروع دوبارهٔ مراحل\n\n"
            "*توجه:* این ربات فقط جنبهٔ آموزشی دارد و توصیهٔ مالی نیست!"
        ),
        "cancel_message": "✅ فرایند لغو شد. برای شروع دوباره /start را وارد کنید.",
        "restart_message": "🔄 جلسه ریست شد. /start را برای شروع تازه وارد کنید!",
        "not_sure": "متوجه نشدم. لطفاً از /start یا منوی زیر استفاده کنید.",
        "ask_amount": (
            "💰 *مرحلهٔ ۱:* چه مقدار (دلار) می‌خواهید *به صورت کلی* سرمایه‌گذاری کنید؟\n\n"
            "_مثال:_ 1000 یا 1200.50"
        ),
        "invalid_amount": "❌ مبلغ نامعتبر. لطفاً فقط عدد وارد کنید (مثلاً 1000 یا 1200.50).",
        "ask_symbol": (
            "💱 *مرحلهٔ ۲:* روی کدام *جفت رمزارز* می‌خواهید سرمایه‌گذاری کنید؟\n\n"
            "_مثال:_ BTC/USDT، ETH/USDT"
        ),
        # ------ Range or Period ------
        "ask_range_or_period": (
            "آیا می‌خواهید یک *بازهٔ تاریخی دقیق* (تاریخ شروع و پایان) مشخص کنید،\n"
            "یا از روش *سنتی دوره (period)* استفاده کنید؟\n\n"
            "عبارت 'range' را وارد کنید تا تاریخ‌های شروع/پایان تعیین شود "
            "(چه تاریخ دقیق مانند `2022-01-01`، چه نسبی مثل `1 year ago`).\n"
            "عبارت 'period' را وارد کنید تا روش دوره‌ای معمول را پی بگیرید (مثلاً '1 year' همراه با "
            "تاریخ شروع اختیاری).\n\n"
            "نمونه:\n"
            "- `range`\n"
            "- `period`"
        ),
        "ask_range_continue": (
            "عالی! الان تاریخ شروع و تاریخ پایان را دریافت می‌کنیم.\n\n"
            "لطفاً هر چیزی تایپ کنید تا ادامه دهیم..."
        ),
        "ask_range_start_instructions": (
            "📅 *بازهٔ تاریخی سفارشی (تاریخ شروع)*\n\n"
            "لطفاً تاریخ شروع خود را وارد کنید. می‌توانید از قالب‌های زیر استفاده کنید:\n"
            "- تاریخ دقیق، مثل `2022-01-01`\n"
            "- عبارت نسبی، مثل `1 year ago`، `6 months ago`، `today`\n\n"
            "مثال‌ها:\n"
            "`2023-01-01`\n"
            "`1 year ago`\n\n"
            "تاریخ شروع را اکنون وارد کنید:"
        ),
        "ask_range_end_instructions": (
            "📅 *بازهٔ تاریخی سفارشی (تاریخ پایان)*\n\n"
            "حالا تاریخ پایان خود را وارد کنید. می‌توانید از قالب‌های زیر استفاده کنید:\n"
            "- تاریخ دقیق، مثل `2023-01-01`\n"
            "- عبارت نسبی، مثل `6 months ago`، `today`\n\n"
            "مثال‌ها:\n"
            "`2023-06-01`\n"
            "`6 months ago`\n"
            "`today`\n\n"
            "تاریخ پایان را اکنون وارد کنید:"
        ),
        # ------ Range parse errors ------
        "range_parse_error_start": (
            "❌ {error}\n"
            "لطفاً دوباره تلاش کنید. مثال: `2022-01-01` یا `6 months ago`"
        ),
        "range_parse_error_end": (
            "❌ {error}\n"
            "لطفاً دوباره امتحان کنید. مثال: `2023-01-01` یا `2 weeks ago` یا `today`"
        ),

        "ask_period": (
            "⏱ *مرحلهٔ ۳:* می‌خواهید در چه بازه‌ای سرمایه‌گذاری کنید؟\n\n"
            "_مثال‌ها:_ ۱ سال، ۶ ماه، ۲ هفته."
        ),
        "ask_custom_start": (
            "📅 آیا می‌خواهید *تاریخ شروع* خاصی تعیین کنید؟\n\n"
            "اگر نه، فرض می‌کنیم این بازه تا امروز است و از امروز برمی‌گردیم.\n"
            "«yes» یا «no» را وارد کنید."
        ),
        "ask_enter_custom_start": (
            "✏️ لطفاً تاریخ شروع را با فرمت `YYYY-MM-DD` وارد کنید.\n\n"
            "_مثال:_ 01-01-2022"
        ),
        "invalid_date": "❌ فرمت تاریخ نامعتبر است. لطفاً از قالب YYYY-MM-DD استفاده کنید.",
        "ask_frequency": (
            "🔁 *مرحلهٔ ۴:* هر چند وقت یک‌بار سرمایه‌گذاری خواهید کرد؟\n\n"
            "_مثال‌ها:_ هفتگی، هر دو هفته، ماهانه، هر ۳ روز."
        ),
        "ask_fee": (
            "💸 *مرحلهٔ ۵:* درصد کارمزد (fee) را وارد کنید (در صورت وجود).\n\n"
            "_مثال:_ `0.1` یعنی کارمزد 0.1%. برای ۰ عدد صفر وارد کنید."
        ),
        "invalid_fee": "❌ درصد کارمزد نامعتبر است. باید عددی غیرمنفی باشد.",
        "calculating": "⌛ *در حال محاسبهٔ عملکرد DCA...* کمی صبر کنید...",
        "final_prompt": "✅ تمام! گزارش نهایی DCA شما:",
        "error_value": "❌ خطا: ",
        "error_unexpected": "❌ خطای پیش‌بینی‌نشده: ",
        "settings_menu": "⚙️ *تنظیمات:* یکی را انتخاب کنید:",
        "set_language_button": "تغییر زبان",
        "back_button": "« بازگشت",
        "choose_lang_button": "انتخاب زبان",
        "language_choice_en": "English",
        "language_choice_es": "Farsi",
    }
}
