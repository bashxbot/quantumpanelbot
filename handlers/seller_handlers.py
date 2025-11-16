"""
Seller panel handlers for Quantum Panel Bot
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import (
    is_seller, get_seller_stats, get_products_for_seller,
    reverse_sessions, active_sessions, seller_alerts,
    session_start_times, update_seller_stats, log_chat
)

logger = logging.getLogger(__name__)

# ====================================================
#                SELLER PANEL
# ====================================================

async def seller_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open seller panel"""
    user_id = update.message.from_user.id
    user = update.message.from_user
    user_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"

    # Check if seller is in an active session
    if user_id in reverse_sessions:
        await update.message.reply_text(
            f"⚠️ *Active Session Detected*\n\n"
            f"👤 {user_name} ({username})\n\n"
            f"Please use /stop to end the current conversation before using other commands.",
            parse_mode="Markdown"
        )
        return

    if not is_seller(user_id):
        await update.message.reply_text(
            f"❌ *ACCESS DENIED*\n\n"
            f"You don't have access to the seller panel.\n\n"
            f"👤 {user_name} ({username})",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="seller_stats"),
         InlineKeyboardButton("📦 Products I Sell", callback_data="seller_products")],
        [InlineKeyboardButton("🔄 Active Chat", callback_data="seller_active_chat"),
         InlineKeyboardButton("🔔 Toggle Alerts", callback_data="seller_toggle_alerts")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="seller_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"💼 *SELLER PANEL*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *Seller:* {user_name}\n"
        f"🆔 *Username:* {username}\n"
        f"🔑 *Seller ID:* `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🎯 Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def open_seller_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open seller panel from callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id

    if not is_seller(user_id):
        await query.message.reply_text("❌ You don't have access to the seller panel.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="seller_stats"),
         InlineKeyboardButton("📦 Products I Sell", callback_data="seller_products")],
        [InlineKeyboardButton("🔄 Active Chat", callback_data="seller_active_chat"),
         InlineKeyboardButton("🔔 Toggle Alerts", callback_data="seller_toggle_alerts")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="seller_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text="💼 Seller Panel\n\nChoose an option:",
        reply_markup=reply_markup
    )

# ====================================================
#                SELLER STATS
# ====================================================

async def seller_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show seller statistics"""
    query = update.callback_query
    await query.answer()

    seller_id = query.from_user.id
    seller = query.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else None
    
    stats = get_seller_stats(seller_id)

    last_users = "\n".join([f"  • `{uid}`" for uid in stats["last_10_users"]]) or "  • None yet"

    username_line = f"🆔 *Username:* {seller_username}\n" if seller_username else ""
    
    message = (
        f"📊 *YOUR STATISTICS*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *Seller:* {seller_name}\n"
        f"{username_line}"
        f"🔑 *ID:* `{seller_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📈 *Performance Metrics:*\n\n"
        f"👥 *Total Users Served:* {stats['total_served']}\n"
        f"💬 *Chats Completed:* {stats['chats_completed']}\n"
        f"📅 *Today's Stats:* {stats['today_stats']}\n"
        f"📆 *Monthly Stats:* {stats['monthly_stats']}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🕐 *Last 10 Handled Users:*\n{last_users}"
    )

    await query.message.reply_text(message, parse_mode="Markdown")

# ====================================================
#            SELLER PRODUCTS
# ====================================================

async def seller_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show products seller is assigned to"""
    query = update.callback_query
    await query.answer()

    seller_id = query.from_user.id
    seller = query.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else None
    
    products = get_products_for_seller(seller_id)

    username_line = f"🆔 *Username:* {seller_username}\n" if seller_username else ""

    if products:
        product_list = "\n".join([f"  🎯 {p}" for p in products])
        message = (
            f"📦 *YOUR PRODUCTS*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Seller:* {seller_name}\n"
            f"{username_line}"
            f"🔑 *ID:* `{seller_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🛍️ *Products You Sell:*\n\n{product_list}"
        )
    else:
        message = (
            f"❌ *NO PRODUCTS ASSIGNED*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Seller:* {seller_name}\n"
            f"{username_line}"
            f"🔑 *ID:* `{seller_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"You are not currently assigned to any products."
        )

    await query.message.reply_text(message, parse_mode="Markdown")

# ====================================================
#            SELLER ACTIVE CHAT
# ====================================================

async def seller_active_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show seller's active chat"""
    query = update.callback_query
    await query.answer()

    seller_id = query.from_user.id
    seller = query.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else None

    username_line = f"🆔 *Seller Username:* {seller_username}\n" if seller_username else ""

    if seller_id in reverse_sessions:
        user_id = reverse_sessions[seller_id]
        session_info = active_sessions[user_id]
        product = session_info["product"]

        keyboard = [
            [InlineKeyboardButton("❌ End Chat", callback_data=f"seller_end_chat_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"🔄 *ACTIVE CHAT SESSION*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"💼 *Seller:* {seller_name}\n"
            f"{username_line}"
            f"🔑 *Seller ID:* `{seller_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer ID:* `{user_id}`\n"
            f"📦 *Product:* {product}\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"💬 Chat is currently active!"
        )

        await query.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        message = (
            f"❌ *NO ACTIVE CHAT*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"💼 *Seller:* {seller_name}\n"
            f"{username_line}"
            f"🔑 *Seller ID:* `{seller_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"You don't have any active conversations."
        )
        await query.message.reply_text(message, parse_mode="Markdown")

# ====================================================
#            SELLER END CHAT
# ====================================================

async def seller_end_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """End seller's active chat"""
    query = update.callback_query
    await query.answer()

    seller_id = query.from_user.id
    seller = query.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else None

    try:
        user_id = int(query.data.split('_')[3])
    except (IndexError, ValueError):
        await query.message.reply_text(
            f"❌ *INVALID REQUEST*\n\n"
            f"Something went wrong. Please try again.",
            parse_mode="Markdown"
        )
        return

    if seller_id not in reverse_sessions or reverse_sessions[seller_id] != user_id:
        await query.message.reply_text(
            f"❌ *CHAT NOT ACTIVE*\n\n"
            f"This chat is no longer active.",
            parse_mode="Markdown"
        )
        return

    session_info = active_sessions[user_id]
    product = session_info["product"]
    start_time = session_start_times.get(user_id, datetime.now())

    update_seller_stats(seller_id, user_id)
    log_chat(user_id, seller_id, product, start_time)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"⚠️ *CONVERSATION ENDED*\n\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"The seller has ended the conversation.\n\n"
                f"💡 If you still need help, tap *Buy Key(s)* again!"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    username_line = f"🆔 *Username:* {seller_username}\n" if seller_username else ""
    
    await query.message.reply_text(
        f"🛑 *CONVERSATION STOPPED*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💼 *Seller:* {seller_name}\n"
        f"{username_line}"
        f"🔑 *Seller ID:* `{seller_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📦 *Product:* {product}\n"
        f"👤 *Customer ID:* `{user_id}`\n\n"
        f"✅ Chat ended successfully!",
        parse_mode="Markdown"
    )

    del reverse_sessions[seller_id]
    del active_sessions[user_id]
    if user_id in session_start_times:
        del session_start_times[user_id]

# ====================================================
#            SELLER TOGGLE ALERTS
# ====================================================

async def seller_toggle_alerts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle seller alert notifications"""
    query = update.callback_query
    await query.answer()

    seller_id = query.from_user.id
    seller = query.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else None
    
    current = seller_alerts.get(seller_id, True)
    seller_alerts[seller_id] = not current

    status = "✅ *Enabled*" if seller_alerts[seller_id] else "🔕 *Disabled*"
    username_line = f"🆔 *Username:* {seller_username}\n" if seller_username else ""
    
    await query.message.reply_text(
        f"🔔 *ALERT SETTINGS UPDATED*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💼 *Seller:* {seller_name}\n"
        f"{username_line}"
        f"🔑 *Seller ID:* `{seller_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📢 *Alerts Status:* {status}",
        parse_mode="Markdown"
    )

# ====================================================
#            SELLER HELP
# ====================================================

async def seller_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show seller help information"""
    query = update.callback_query
    await query.answer()

    seller = query.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else None
    seller_id = seller.id

    username_line = f"🆔 *Username:* {seller_username}\n" if seller_username else ""

    help_text = (
        f"ℹ️ *SELLER HELP & COMMANDS*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💼 *Seller:* {seller_name}\n"
        f"{username_line}"
        f"🔑 *Seller ID:* `{seller_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📱 *Available Commands:*\n\n"
        f"  • `/seller` - Open seller panel\n"
        f"  • `/stop` - End active conversation\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✨ *What You Can Do:*\n\n"
        f"  ✅ Accept connection requests\n"
        f"  💬 Chat with users\n"
        f"  📊 View your statistics\n"
        f"  📦 See products you sell\n"
        f"  🔔 Toggle request alerts"
    )

    await query.message.reply_text(help_text, parse_mode="Markdown")