# data_store.py

import logging

logger = logging.getLogger(__name__)

class BotState:
    """Enum-like class for conversation states."""
    IDLE = "IDLE"
    LANG_SELECT = "LANG_SELECT"

    # Old approach
    ENTERING_AMOUNT = "ENTERING_AMOUNT"
    ENTERING_SYMBOL = "ENTERING_SYMBOL"
    ASK_DATE_RANGE_OR_PERIOD = "ASK_DATE_RANGE_OR_PERIOD"  # <-- NEW
    ENTERING_PERIOD = "ENTERING_PERIOD"
    ASK_CUSTOM_START = "ASK_CUSTOM_START"
    ENTERING_CUSTOM_START = "ENTERING_CUSTOM_START"

    # Fully custom range
    ASK_CUSTOM_BOTH_RANGE = "ASK_CUSTOM_BOTH_RANGE"  # <-- NEW
    ENTERING_RANGE_START = "ENTERING_RANGE_START"    # <-- NEW
    ENTERING_RANGE_END = "ENTERING_RANGE_END"        # <-- NEW

    ENTERING_FREQUENCY = "ENTERING_FREQUENCY"
    ENTERING_FEE = "ENTERING_FEE"
    CALCULATE = "CALCULATE"

class UserSession:
    """
    Stores all user-specific conversation data.
    Fields:
        - state (BotState)
        - lang (str: 'en' or 'fa')
        - total_investment (float)
        - symbol (str)
        - period_str (str)
        - custom_start_date (datetime or None)
        - custom_range_end_date (datetime or None)
        - frequency_str (str)
        - fee_percent (float)
    """
    def __init__(self):
        self.state = BotState.IDLE
        self.lang = 'en'  # default
        self.total_investment = 0.0
        self.symbol = ""
        self.period_str = ""
        self.custom_start_date = None
        self.custom_range_end_date = None
        self.frequency_str = ""
        self.fee_percent = 0.0

class DataStore:
    """In-memory user session store."""
    def __init__(self):
        self.user_sessions = {}

    def get_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession()
        return self.user_sessions[user_id]

    def reset_session(self, user_id):
        logger.info(f"Resetting session for user_id={user_id}")
        self.user_sessions[user_id] = UserSession()
        return self.user_sessions[user_id]
