"""
Handlers package initialization
Exports all handler functions for the Telegram bot
"""

# User handlers
from .user_handlers import (
    start,
    buy_keys_callback,
    product_selection_callback,
    connect_with_seller_callback,
    accept_request_callback,
    handle_message,
    stop
)

# Seller handlers
from .seller_handlers import (
    seller_panel,
    open_seller_panel_callback,
    seller_stats_callback,
    seller_products_callback,
    seller_active_chat_callback,
    seller_end_chat_callback,
    seller_toggle_alerts_callback,
    seller_help_callback
)

# Admin handlers - Part 1
from .admin_handlers import (
    admin_panel,
    open_admin_panel_callback,
    admin_manage_sellers_callback,
    admin_view_sellers_callback,
    admin_manage_products_callback,
    admin_remove_product_callback,
    confirm_remove_product_callback,
    admin_view_products_callback,
    admin_assign_sellers_callback,
    admin_remove_seller_product_callback,
    admin_broadcast_callback,
    admin_global_stats_callback,
    admin_monitor_sessions_callback,
    force_stop_session_callback,
    admin_back_callback
)

# Admin handlers - Part 2
from .admin_handlers_part2 import (
    admin_logs_callback,
    view_chat_logs_callback,
    view_seller_performance_callback,
    admin_export_callback,
    export_users_callback,
    export_sellers_callback,
    export_products_callback,
    export_chats_callback,
    admin_emergency_callback,
    emergency_disable_buy_callback,
    emergency_enable_buy_callback,
    emergency_block_user_callback,
    emergency_unblock_user_callback
)

__all__ = [
    # User handlers
    'start', 'buy_keys_callback', 'product_selection_callback',
    'connect_with_seller_callback', 'accept_request_callback',
    'handle_message', 'stop',
    # Seller handlers
    'seller_panel', 'open_seller_panel_callback', 'seller_stats_callback', 'seller_products_callback',
    'seller_active_chat_callback', 'seller_end_chat_callback',
    'seller_toggle_alerts_callback', 'seller_help_callback',
    # Admin handlers
    'admin_panel', 'open_admin_panel_callback', 'admin_manage_sellers_callback', 'admin_view_sellers_callback',
    'admin_manage_products_callback', 'admin_remove_product_callback',
    'confirm_remove_product_callback', 'admin_view_products_callback',
    'admin_assign_sellers_callback', 'admin_remove_seller_product_callback',
    'admin_broadcast_callback', 'admin_global_stats_callback',
    'admin_monitor_sessions_callback', 'force_stop_session_callback',
    'admin_logs_callback', 'view_chat_logs_callback', 'view_seller_performance_callback',
    'admin_export_callback', 'export_users_callback', 'export_sellers_callback',
    'export_products_callback', 'export_chats_callback',
    'admin_emergency_callback', 'emergency_disable_buy_callback',
    'emergency_enable_buy_callback', 'emergency_block_user_callback',
    'emergency_unblock_user_callback', 'admin_back_callback'
]