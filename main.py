"""
Quantum Panel - Telegram Bot
Main entry point with clean modular structure
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

# Import configuration
from config import (
    BOT_TOKEN,
    WAITING_SELLER_ID, WAITING_PRODUCT_NAME, WAITING_PRODUCT_DESC,
    WAITING_PRODUCT_IMAGE, WAITING_PRODUCT_SELLERS, WAITING_BROADCAST_MESSAGE,
    WAITING_BLOCK_USER_ID, WAITING_UNBLOCK_USER_ID, WAITING_REMOVE_SELLER_ID,
    WAITING_ASSIGN_PRODUCT_SELLERS, WAITING_REMOVE_SELLER_FROM_PRODUCT
)

# Import handlers
from handlers import (
    # User handlers
    start, buy_keys_callback, product_selection_callback,
    connect_with_seller_callback, accept_request_callback,
    handle_message, stop,
    # Seller handlers
    seller_panel, seller_stats_callback, seller_products_callback,
    seller_active_chat_callback, seller_end_chat_callback,
    seller_toggle_alerts_callback, seller_help_callback,
    # Admin handlers
    admin_panel, admin_manage_sellers_callback, admin_view_sellers_callback,
    admin_manage_products_callback, admin_remove_product_callback,
    confirm_remove_product_callback, admin_view_products_callback,
    admin_assign_sellers_callback, admin_remove_seller_product_callback,
    admin_broadcast_callback, admin_global_stats_callback,
    admin_monitor_sessions_callback, force_stop_session_callback,
    admin_logs_callback, view_chat_logs_callback, view_seller_performance_callback,
    admin_export_callback, export_users_callback, export_sellers_callback,
    export_products_callback, export_chats_callback,
    admin_emergency_callback, emergency_disable_buy_callback,
    emergency_enable_buy_callback, admin_back_callback
)

# Import conversation handlers
from conversations import (
    admin_add_seller_callback, receive_seller_id,
    admin_remove_seller_callback, receive_remove_seller_id,
    admin_add_product_callback, receive_product_name,
    receive_product_desc, receive_product_image, receive_product_sellers,
    select_product_assign_callback, receive_assign_sellers,
    select_product_remove_seller_callback, receive_remove_seller_from_product,
    broadcast_users_callback, broadcast_sellers_callback,
    broadcast_everyone_callback, receive_broadcast_message,
    emergency_block_user_callback, receive_block_user_id,
    emergency_unblock_user_callback, receive_unblock_user_id,
    cancel
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================================================
#                    MAIN FUNCTION
# ====================================================

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        print("\n❌ ERROR: BOT_TOKEN is required!")
        print("Please set BOT_TOKEN environment variable with your Telegram bot token.\n")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # ====================================================
    #            COMMAND HANDLERS
    # ====================================================
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("seller", seller_panel))
    application.add_handler(CommandHandler("admin", admin_panel))

    # ====================================================
    #            USER FLOW CALLBACKS
    # ====================================================
    application.add_handler(CallbackQueryHandler(buy_keys_callback, pattern="^buy_keys$"))
    
    # Admin/Seller panel quick access
    from handlers.admin_handlers import open_admin_panel_callback
    from handlers.seller_handlers import open_seller_panel_callback
    application.add_handler(CallbackQueryHandler(open_admin_panel_callback, pattern="^open_admin_panel$"))
    application.add_handler(CallbackQueryHandler(open_seller_panel_callback, pattern="^open_seller_panel$"))
    application.add_handler(CallbackQueryHandler(product_selection_callback, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(connect_with_seller_callback, pattern="^connect_"))
    application.add_handler(CallbackQueryHandler(accept_request_callback, pattern="^accept_"))

    # ====================================================
    #            SELLER PANEL CALLBACKS
    # ====================================================
    application.add_handler(CallbackQueryHandler(seller_stats_callback, pattern="^seller_stats$"))
    application.add_handler(CallbackQueryHandler(seller_products_callback, pattern="^seller_products$"))
    application.add_handler(CallbackQueryHandler(seller_active_chat_callback, pattern="^seller_active_chat$"))
    application.add_handler(CallbackQueryHandler(seller_end_chat_callback, pattern="^seller_end_chat_"))
    application.add_handler(CallbackQueryHandler(seller_toggle_alerts_callback, pattern="^seller_toggle_alerts$"))
    application.add_handler(CallbackQueryHandler(seller_help_callback, pattern="^seller_help$"))

    # ====================================================
    #            ADMIN PANEL CALLBACKS
    # ====================================================
    application.add_handler(CallbackQueryHandler(admin_manage_sellers_callback, pattern="^admin_manage_sellers$"))
    application.add_handler(CallbackQueryHandler(admin_manage_products_callback, pattern="^admin_manage_products$"))
    application.add_handler(CallbackQueryHandler(admin_broadcast_callback, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_global_stats_callback, pattern="^admin_global_stats$"))
    application.add_handler(CallbackQueryHandler(admin_monitor_sessions_callback, pattern="^admin_monitor_sessions$"))
    application.add_handler(CallbackQueryHandler(admin_logs_callback, pattern="^admin_logs$"))
    application.add_handler(CallbackQueryHandler(admin_export_callback, pattern="^admin_export$"))
    application.add_handler(CallbackQueryHandler(admin_emergency_callback, pattern="^admin_emergency$"))
    application.add_handler(CallbackQueryHandler(admin_back_callback, pattern="^admin_back$"))

    # Manage sellers callbacks
    from handlers.admin_handlers import (
        admin_select_product_add_seller_callback,
        admin_select_product_remove_seller_callback,
        admin_select_product_view_sellers_callback
    )
    application.add_handler(CallbackQueryHandler(admin_select_product_add_seller_callback, pattern="^admin_select_product_add_seller$"))
    application.add_handler(CallbackQueryHandler(admin_select_product_remove_seller_callback, pattern="^admin_select_product_remove_seller$"))
    application.add_handler(CallbackQueryHandler(admin_select_product_view_sellers_callback, pattern="^admin_select_product_view_sellers$"))
    application.add_handler(CallbackQueryHandler(admin_view_sellers_callback, pattern="^viewsellers_of_"))

    # Manage products callbacks
    application.add_handler(CallbackQueryHandler(admin_view_products_callback, pattern="^admin_view_products$"))
    application.add_handler(CallbackQueryHandler(admin_remove_product_callback, pattern="^admin_remove_product$"))
    application.add_handler(CallbackQueryHandler(confirm_remove_product_callback, pattern="^remove_product_"))
    application.add_handler(CallbackQueryHandler(admin_assign_sellers_callback, pattern="^admin_assign_sellers$"))
    application.add_handler(CallbackQueryHandler(admin_remove_seller_product_callback, pattern="^admin_remove_seller_product$"))

    # Monitor sessions callbacks
    application.add_handler(CallbackQueryHandler(force_stop_session_callback, pattern="^force_stop_"))

    # Logs callbacks
    application.add_handler(CallbackQueryHandler(view_chat_logs_callback, pattern="^view_chat_logs$"))
    application.add_handler(CallbackQueryHandler(view_seller_performance_callback, pattern="^view_seller_performance$"))

    # Export callbacks
    application.add_handler(CallbackQueryHandler(export_users_callback, pattern="^export_users$"))
    application.add_handler(CallbackQueryHandler(export_sellers_callback, pattern="^export_sellers$"))
    application.add_handler(CallbackQueryHandler(export_products_callback, pattern="^export_products$"))
    application.add_handler(CallbackQueryHandler(export_chats_callback, pattern="^export_chats$"))

    # Emergency tools callbacks
    application.add_handler(CallbackQueryHandler(emergency_disable_buy_callback, pattern="^emergency_disable_buy$"))
    application.add_handler(CallbackQueryHandler(emergency_enable_buy_callback, pattern="^emergency_enable_buy$"))

    # ====================================================
    #            CONVERSATION HANDLERS
    # ====================================================

    # Add seller conversation
    add_seller_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_seller_callback, pattern="^addseller_to_")],
        states={
            WAITING_SELLER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_seller_id)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(add_seller_conv)

    # Remove seller conversation
    remove_seller_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_remove_seller_callback, pattern="^remseller_from_")],
        states={
            WAITING_REMOVE_SELLER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_remove_seller_id)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(remove_seller_conv)

    # Add product conversation
    add_product_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_product_callback, pattern="^admin_add_product$")],
        states={
            WAITING_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_name)],
            WAITING_PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_desc)],
            WAITING_PRODUCT_IMAGE: [MessageHandler(filters.PHOTO, receive_product_image)],
            WAITING_PRODUCT_SELLERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product_sellers)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(add_product_conv)

    # Assign sellers to product conversation
    assign_sellers_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_product_assign_callback, pattern="^assign_to_")],
        states={
            WAITING_ASSIGN_PRODUCT_SELLERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_assign_sellers)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(assign_sellers_conv)

    # Remove seller from product conversation
    remove_seller_product_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_product_remove_seller_callback, pattern="^rmseller_from_")],
        states={
            WAITING_REMOVE_SELLER_FROM_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_remove_seller_from_product)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(remove_seller_product_conv)

    # Broadcast conversation
    broadcast_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(broadcast_users_callback, pattern="^broadcast_users$"),
            CallbackQueryHandler(broadcast_sellers_callback, pattern="^broadcast_sellers$"),
            CallbackQueryHandler(broadcast_everyone_callback, pattern="^broadcast_everyone$")
        ],
        states={
            WAITING_BROADCAST_MESSAGE: [
                MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, receive_broadcast_message)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(broadcast_conv)

    # Block user conversation
    block_user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(emergency_block_user_callback, pattern="^emergency_block_user$")],
        states={
            WAITING_BLOCK_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_block_user_id)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(block_user_conv)

    # Unblock user conversation
    unblock_user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(emergency_unblock_user_callback, pattern="^emergency_unblock_user$")],
        states={
            WAITING_UNBLOCK_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_unblock_user_id)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(unblock_user_conv)

    # ====================================================
    #            REGULAR MESSAGE HANDLER (MUST BE LAST)
    # ====================================================
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("Quantum Panel bot is starting...")
    print("\n✅ Quantum Panel bot is running!")
    print("Press Ctrl+C to stop\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
