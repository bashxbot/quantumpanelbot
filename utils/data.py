"""
Data storage for Quantum Panel Bot
"""

# ====================================================
#                    DATA STORAGE
# ====================================================

# Active sessions: user_id -> {"seller_id": admin_id, "product": product_name}
active_sessions = {}

# Reverse sessions: admin_id -> user_id
reverse_sessions = {}

# Pending requests: user_id -> {"product": product_name}
pending_requests = {}

# User product selection: user_id -> product_name (temporary storage)
user_product_selection = {}

# Seller alerts: seller_id -> bool (True = enabled, False = disabled)
seller_alerts = {}

# Seller statistics: seller_id -> {total_served, chats_completed, last_10_users, ...}
seller_stats = {}

# Chat history: [{user_id, seller_id, product, start_time, end_time, messages}]
chat_history = []

# All users who've started the bot
all_users = set()

# Blocked users
blocked_users = set()

# Buy button enabled/disabled
buy_button_enabled = True

# Session start times: user_id -> datetime
session_start_times = {}

# Temporary data for multi-step processes
temp_data = {}