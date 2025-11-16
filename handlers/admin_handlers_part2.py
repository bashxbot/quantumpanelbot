"""
Admin panel handlers for Quantum Panel Bot (Part 2)
Additional functions for logs, exports, and emergency tools
"""

import logging
import csv
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMINS, SELLERS, PRODUCT_SELLERS, PRODUCT_DESCRIPTIONS
from utils import (
    get_seller_stats, chat_history, all_users, blocked_users,
    active_sessions, reverse_sessions, session_start_times
)
import utils.data

logger = logging.getLogger(__name__)

# ====================================================
#                    LOGS
# ====================================================

async def admin_logs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show logs menu"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📜 Chat Logs", callback_data="view_chat_logs"),
         InlineKeyboardButton("📊 Seller Performance", callback_data="view_seller_performance")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="📝 Logs Menu",
        reply_markup=reply_markup
    )

async def view_chat_logs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View recent chat logs"""
    query = update.callback_query
    await query.answer()

    if not chat_history:
        await query.message.reply_text("❌ No chat logs available.")
        return

    recent_logs = chat_history[-10:]
    message = "📜 Recent Chat Logs (Last 10):\n\n"

    for log in recent_logs:
        user_info = log.get('user_info', {})
        seller_info = log.get('seller_info', {})
        user_name = user_info.get('full_name', 'N/A')
        user_username = f"(@{user_info.get('username')})" if user_info.get('username') else ''
        seller_name = seller_info.get('full_name', 'N/A')
        seller_username = f"(@{seller_info.get('username')})" if seller_info.get('username') else ''

        start = log["start_time"].strftime("%Y-%m-%d %H:%M") if isinstance(log["start_time"], datetime) else "Unknown"
        message += (
            f"👤 User: {user_name} {user_username}\n"
            f"🧑‍💼 Seller: {seller_name} {seller_username}\n"
            f"📦 Product: {log['product']}\n"
            f"⏳ Start: {start}\n"
            f"--------------------\n"
        )

    await query.message.reply_text(message)

async def view_seller_performance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View seller performance"""
    query = update.callback_query
    await query.answer()

    message = "📊 *SELLER PERFORMANCE*\n\n━━━━━━━━━━━━━━━━━\n\n"

    for seller_id in set(SELLERS + ADMINS):
        stats = get_seller_stats(seller_id)
        
        # Fetch seller details
        try:
            seller_chat = await query.message.chat.get_chat(seller_id)
            seller_name = seller_chat.full_name or "Unknown"
            seller_username = f"@{seller_chat.username}" if seller_chat.username else ""
        except Exception:
            seller_name = "Unknown"
            seller_username = ""

        message += (
            f"🧑‍💼 *Seller:* {seller_name} {seller_username}\n"
            f"  🔑 *ID:* `{seller_id}`\n"
            f"  📈 *Total Served:* {stats['total_served']}\n"
            f"  ✅ *Completed:* {stats['chats_completed']}\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
        )

    await query.message.reply_text(message, parse_mode="Markdown")

# ====================================================
#                EXPORT DATA
# ====================================================

async def admin_export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show export menu"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("👥 Export Users", callback_data="export_users"),
         InlineKeyboardButton("🧑‍💼 Export Sellers", callback_data="export_sellers")],
        [InlineKeyboardButton("📦 Export Products", callback_data="export_products"),
         InlineKeyboardButton("💬 Export Chats", callback_data="export_chats")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="📤 Export Data Menu",
        reply_markup=reply_markup
    )

async def export_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export users data"""
    query = update.callback_query
    await query.answer()

    filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['User ID'])
        for user_id in all_users:
            writer.writerow([user_id])

    try:
        with open(filename, 'rb') as f:
            await context.bot.send_document(chat_id=query.from_user.id, document=f, filename=filename)
        os.remove(filename)
    except Exception as e:
        logger.error(f"Failed to export users: {e}")
        await query.message.reply_text("❌ Failed to export users.")

async def export_sellers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export sellers data"""
    query = update.callback_query
    await query.answer()

    filename = f"sellers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Seller ID'])
        for seller_id in SELLERS:
            writer.writerow([seller_id])

    try:
        with open(filename, 'rb') as f:
            await context.bot.send_document(chat_id=query.from_user.id, document=f, filename=filename)
        os.remove(filename)
    except Exception as e:
        logger.error(f"Failed to export sellers: {e}")
        await query.message.reply_text("❌ Failed to export sellers.")

async def export_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export products data"""
    query = update.callback_query
    await query.answer()

    filename = f"products_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Product Name', 'Description', 'Sellers'])

        for product, sellers in PRODUCT_SELLERS.items():
            description = PRODUCT_DESCRIPTIONS.get(product, "")
            seller_list = ', '.join(map(str, sellers))
            writer.writerow([product, description, seller_list])

    try:
        with open(filename, 'rb') as f:
            await context.bot.send_document(chat_id=query.from_user.id, document=f, filename=filename)
        os.remove(filename)
    except Exception as e:
        logger.error(f"Failed to export products: {e}")
        await query.message.reply_text("❌ Failed to export products.")

async def export_chats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export chat history"""
    query = update.callback_query
    await query.answer()

    filename = f"chats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['User ID', 'Seller ID', 'Product', 'Start Time', 'End Time'])

        for chat in chat_history:
            start = chat["start_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(chat["start_time"], datetime) else "Unknown"
            end = chat["end_time"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(chat.get("end_time"), datetime) else "Ongoing"
            writer.writerow([chat["user_id"], chat["seller_id"], chat["product"], start, end])

    try:
        with open(filename, 'rb') as f:
            await context.bot.send_document(chat_id=query.from_user.id, document=f, filename=filename)
        os.remove(filename)
    except Exception as e:
        logger.error(f"Failed to export chats: {e}")
        await query.message.reply_text("❌ Failed to export chats.")

# ====================================================
#            EMERGENCY TOOLS
# ====================================================

async def admin_emergency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show emergency tools menu"""
    query = update.callback_query
    await query.answer()

    buy_status = "🟢 *ENABLED*" if utils.data.buy_button_enabled else "🔴 *DISABLED*"

    keyboard = [
        [InlineKeyboardButton("🔴 Disable Buy", callback_data="emergency_disable_buy"),
         InlineKeyboardButton("🟢 Enable Buy", callback_data="emergency_enable_buy")],
        [InlineKeyboardButton("🚫 Block User", callback_data="emergency_block_user"),
         InlineKeyboardButton("✅ Unblock User", callback_data="emergency_unblock_user")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=(
            f"🚨 *EMERGENCY CONTROL PANEL*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🔘 *Buy Button Status:* {buy_status}\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚡ Use these tools to manage emergency situations:"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def emergency_disable_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disable buy button"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"(@{admin.username})" if admin.username else "No username"

    import utils.data
    utils.data.buy_button_enabled = False

    await query.message.reply_text(
        f"🔴 *BUY BUTTON DISABLED*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"⚠️ The buy feature has been disabled globally.\n"
        f"Users cannot create new purchase requests.\n\n"
        f"👤 *Action by:* {admin_name} {admin_username}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ Change applied successfully!",
        parse_mode="Markdown"
    )

async def emergency_enable_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable buy button"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"(@{admin.username})" if admin.username else "No username"

    import utils.data
    utils.data.buy_button_enabled = True

    await query.message.reply_text(
        f"🟢 *BUY BUTTON ENABLED*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ The buy feature has been enabled globally.\n"
        f"Users can now create purchase requests.\n\n"
        f"👤 *Action by:* {admin_name} {admin_username}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ Change applied successfully!",
        parse_mode="Markdown"
    )

async def emergency_block_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start block user conversation"""
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "🚫 Block User\n\n"
        "Please send the User ID to block.\n"
        "Use /cancel to abort."
    )

    from config import WAITING_BLOCK_USER_ID
    return WAITING_BLOCK_USER_ID

async def emergency_unblock_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start unblock user conversation"""
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "✅ Unblock User\n\n"
        "Please send the User ID to unblock.\n"
        "Use /cancel to abort."
    )

    from config import WAITING_UNBLOCK_USER_ID
    return WAITING_UNBLOCK_USER_ID