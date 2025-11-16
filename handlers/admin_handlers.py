"""
Admin panel handlers for Quantum Panel Bot (Part 1)
"""

import logging
import csv
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import ADMINS, SELLERS, PRODUCT_SELLERS, PRODUCT_DESCRIPTIONS, PRODUCT_IMAGES
from utils import (
    is_admin, get_seller_stats, active_sessions, reverse_sessions,
    session_start_times, chat_history, all_users, blocked_users,
    log_chat, seller_stats
)
import utils.data

logger = logging.getLogger(__name__)

# ====================================================
#                ADMIN PANEL MAIN
# ====================================================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open admin panel"""
    user_id = update.message.from_user.id
    user = update.message.from_user
    user_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"

    # Check if admin is in an active session
    if user_id in reverse_sessions:
        await update.message.reply_text(
            f"⚠️ *Active Session Detected*\n\n"
            f"👤 {user_name} ({username})\n\n"
            f"Please use /stop to end the current conversation before using other commands.",
            parse_mode="Markdown"
        )
        return

    if not is_admin(user_id):
        await update.message.reply_text(
            f"❌ *ACCESS DENIED*\n\n"
            f"You don't have access to the admin panel.\n\n"
            f"👤 {user_name} ({username})",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton("🔧 Manage Sellers", callback_data="admin_manage_sellers"),
         InlineKeyboardButton("🛍 Manage Products", callback_data="admin_manage_products")],
        [InlineKeyboardButton("📨 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton("📊 Global Statistics", callback_data="admin_global_stats")],
        [InlineKeyboardButton("🧵 Monitor Sessions", callback_data="admin_monitor_sessions"),
         InlineKeyboardButton("📝 Logs", callback_data="admin_logs")],
        [InlineKeyboardButton("📤 Export Data", callback_data="admin_export"),
         InlineKeyboardButton("🚨 Emergency Tools", callback_data="admin_emergency")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🔧 *ADMIN CONTROL PANEL*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *Admin:* {user_name}\n"
        f"🆔 *Username:* {username}\n"
        f"🔑 *Admin ID:* `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"⚡ Choose an administrative function:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def open_admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open admin panel from callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = query.from_user
    user_name = user.full_name
    username = f"@{user.username}" if user.username else None

    if not is_admin(user_id):
        username_line = f"🆔 *Username:* {username}\n" if username else ""
        await query.message.reply_text(
            f"❌ *ACCESS DENIED*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *User:* {user_name}\n"
            f"{username_line}"
            f"🔑 *User ID:* `{user_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"You don't have access to the admin panel.",
            parse_mode="Markdown"
        )
        return

    keyboard = [
        [InlineKeyboardButton("🔧 Manage Sellers", callback_data="admin_manage_sellers"),
         InlineKeyboardButton("🛍 Manage Products", callback_data="admin_manage_products")],
        [InlineKeyboardButton("📨 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton("📊 Global Statistics", callback_data="admin_global_stats")],
        [InlineKeyboardButton("🧵 Monitor Sessions", callback_data="admin_monitor_sessions"),
         InlineKeyboardButton("📝 Logs", callback_data="admin_logs")],
        [InlineKeyboardButton("📤 Export Data", callback_data="admin_export"),
         InlineKeyboardButton("🚨 Emergency Tools", callback_data="admin_emergency")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    username_line = f"🆔 *Username:* {username}\n" if username else ""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"🔧 *ADMIN CONTROL PANEL*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {user_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{user_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚡ Choose an administrative function:"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ====================================================
#            MANAGE SELLERS - MENU
# ====================================================

async def admin_manage_sellers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show seller management menu"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    keyboard = [
        [InlineKeyboardButton("➕ Add Seller to Product", callback_data="admin_select_product_add_seller"),
         InlineKeyboardButton("➖ Remove Seller from Product", callback_data="admin_select_product_remove_seller")],
        [InlineKeyboardButton("👁 View Sellers by Product", callback_data="admin_select_product_view_sellers")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=(
            f"🔧 *MANAGE SELLERS*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚙️ Choose a seller management option:"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def admin_select_product_add_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select product to add seller to"""
    query = update.callback_query
    await query.answer()

    if not PRODUCT_SELLERS:
        await query.message.reply_text("❌ No products available.")
        return

    keyboard = []
    for product in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(product, callback_data=f"addseller_to_{product}")])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data="admin_manage_sellers")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Select a product to add seller to:", reply_markup=reply_markup)

async def admin_select_product_remove_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select product to remove seller from"""
    query = update.callback_query
    await query.answer()

    if not PRODUCT_SELLERS:
        await query.message.reply_text("❌ No products available.")
        return

    keyboard = []
    for product in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(product, callback_data=f"remseller_from_{product}")])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data="admin_manage_sellers")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Select a product to remove seller from:", reply_markup=reply_markup)

async def admin_select_product_view_sellers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select product to view sellers"""
    query = update.callback_query
    await query.answer()

    if not PRODUCT_SELLERS:
        await query.message.reply_text("❌ No products available.")
        return

    keyboard = []
    for product in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(product, callback_data=f"viewsellers_of_{product}")])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data="admin_manage_sellers")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Select a product to view sellers:", reply_markup=reply_markup)

async def admin_view_sellers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View sellers of selected product"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    try:
        product_name = query.data.split('_', 2)[2]
    except (IndexError, ValueError):
        await query.message.reply_text("❌ *Invalid product.*", parse_mode="Markdown")
        return

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    if product_name in PRODUCT_SELLERS and PRODUCT_SELLERS[product_name]:
        # Fetch seller details
        seller_list = []
        for sid in PRODUCT_SELLERS[product_name]:
            try:
                seller_chat = await query.message.get_bot().get_chat(sid)
                seller_name = seller_chat.full_name or "Unknown"
                seller_username = f"@{seller_chat.username}" if seller_chat.username else ""
                seller_info = f"  👤 {seller_name}"
                if seller_username:
                    seller_info += f" {seller_username}"
                seller_info += f"\n     🔑 ID: `{sid}`"
                seller_list.append(seller_info)
            except Exception as e:
                logger.error(f"Failed to fetch seller {sid}: {e}")
                seller_list.append(f"  👤 Unknown Seller\n     🔑 ID: `{sid}`")
        
        sellers_text = "\n\n".join(seller_list)
        message = (
            f"👁 *SELLERS FOR PRODUCT*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📦 *Product:* {product_name}\n\n"
            f"👥 *Assigned Sellers:*\n\n{sellers_text}"
        )
    else:
        message = (
            f"❌ *NO SELLERS ASSIGNED*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📦 *Product:* {product_name}\n\n"
            f"No sellers are currently assigned to this product."
        )

    await query.message.reply_text(message, parse_mode="Markdown")

# ====================================================
#            MANAGE PRODUCTS - MENU
# ====================================================

async def admin_manage_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product management menu"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    keyboard = [
        [InlineKeyboardButton("➕ Add Product", callback_data="admin_add_product"),
         InlineKeyboardButton("➖ Remove Product", callback_data="admin_remove_product")],
        [InlineKeyboardButton("🧑‍💼 Assign Sellers", callback_data="admin_assign_sellers"),
         InlineKeyboardButton("🚫 Remove Seller", callback_data="admin_remove_seller_product")],
        [InlineKeyboardButton("📦 View Products", callback_data="admin_view_products")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=(
            f"🛍 *MANAGE PRODUCTS*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📦 Choose a product management option:"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def admin_remove_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product removal menu"""
    query = update.callback_query
    await query.answer()

    if not PRODUCT_SELLERS:
        await query.message.reply_text("❌ No products to remove.")
        return

    keyboard = []
    for product in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(product, callback_data=f"remove_product_{product}")])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data="admin_manage_products")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Select a product to remove:", reply_markup=reply_markup)

async def confirm_remove_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and remove product"""
    query = update.callback_query
    await query.answer()

    try:
        product_name = query.data.split('_', 2)[2]
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Invalid product.")
        return

    if product_name in PRODUCT_SELLERS:
        del PRODUCT_SELLERS[product_name]
        if product_name in PRODUCT_DESCRIPTIONS:
            del PRODUCT_DESCRIPTIONS[product_name]
        if product_name in PRODUCT_IMAGES:
            del PRODUCT_IMAGES[product_name]

        await query.message.reply_text(f"✅ Product '{product_name}' removed successfully.")
    else:
        await query.message.reply_text("❌ Product not found.")

async def admin_view_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all products"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    if PRODUCT_SELLERS:
        product_list = []
        for product, sellers in PRODUCT_SELLERS.items():
            if sellers:
                seller_details = []
                for sid in sellers:
                    try:
                        seller_chat = await context.bot.get_chat(sid)
                        seller_name = seller_chat.full_name or "Unknown"
                        seller_username = f"@{seller_chat.username}" if seller_chat.username else ""
                        seller_info = f"{seller_name}"
                        if seller_username:
                            seller_info += f" {seller_username}"
                        seller_info += f" (`{sid}`)"
                        seller_details.append(seller_info)
                    except Exception as e:
                        logger.error(f"Failed to fetch seller {sid}: {e}")
                        seller_details.append(f"`{sid}`")
                seller_list = ", ".join(seller_details)
            else:
                seller_list = "None"
            product_list.append(f"📦 *{product}*\n  👥 Sellers: {seller_list}")

        message = (
            f"📦 *ALL PRODUCTS*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🛍️ *Registered Products:*\n\n" + "\n\n".join(product_list)
        )
    else:
        message = (
            f"❌ *NO PRODUCTS REGISTERED*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"No products have been registered yet."
        )

    await query.message.reply_text(message, parse_mode="Markdown")

async def admin_assign_sellers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product selection for assigning sellers"""
    query = update.callback_query
    await query.answer()

    if not PRODUCT_SELLERS:
        await query.message.reply_text("❌ No products available.")
        return

    keyboard = []
    for product in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(product, callback_data=f"assign_to_{product}")])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data="admin_manage_products")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Select a product to assign sellers:", reply_markup=reply_markup)

async def admin_remove_seller_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product selection for removing sellers"""
    query = update.callback_query
    await query.answer()

    if not PRODUCT_SELLERS:
        await query.message.reply_text("❌ No products available.")
        return

    keyboard = []
    for product in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(product, callback_data=f"rmseller_from_{product}")])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data="admin_manage_products")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Select a product to remove sellers from:", reply_markup=reply_markup)

# ====================================================
#                BROADCAST - MENU
# ====================================================

async def admin_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show broadcast menu"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    keyboard = [
        [InlineKeyboardButton("📢 To Users", callback_data="broadcast_users"),
         InlineKeyboardButton("📢 To Sellers", callback_data="broadcast_sellers")],
        [InlineKeyboardButton("📢 To Everyone", callback_data="broadcast_everyone")],
        [InlineKeyboardButton("« Back", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=(
            f"📨 *BROADCAST MESSAGE*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📣 Choose your broadcast audience:"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ====================================================
#            GLOBAL STATISTICS
# ====================================================

async def admin_global_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show global statistics"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    total_users = len(all_users)
    active_users = len(active_sessions)
    total_chats = len(chat_history)
    closed_chats = sum(1 for chat in chat_history if chat["end_time"] is not None)

    product_requests = {}
    for chat in chat_history:
        product = chat["product"]
        product_requests[product] = product_requests.get(product, 0) + 1

    seller_rankings = {}
    for seller_id in set(SELLERS + ADMINS):
        stats = get_seller_stats(seller_id)
        seller_rankings[seller_id] = stats["chats_completed"]

    top_sellers = sorted(seller_rankings.items(), key=lambda x: x[1], reverse=True)[:5]

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    message = (
        f"📊 *GLOBAL STATISTICS*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *Admin:* {admin_name}\n"
        f"{username_line}"
        f"🔑 *Admin ID:* `{admin_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📈 *System Overview:*\n\n"
        f"👥 *Total Users:* {total_users}\n"
        f"🔄 *Active Sessions:* {active_users}\n"
        f"💬 *Total Chats:* {total_chats}\n"
        f"✅ *Closed Chats:* {closed_chats}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📦 *Product-wise Requests:*\n\n"
    )

    if product_requests:
        for product, count in product_requests.items():
            message += f"  🎯 {product}: *{count}*\n"
    else:
        message += "  • No requests yet\n"

    message += f"\n━━━━━━━━━━━━━━━━━\n🏆 *Top 5 Sellers:*\n\n"
    
    if top_sellers:
        for idx, (seller_id, count) in enumerate(top_sellers, 1):
            message += f"  {idx}. Seller `{seller_id}`: *{count}* chats\n"
    else:
        message += "  • No seller data yet\n"

    await query.message.reply_text(message, parse_mode="Markdown")

# ====================================================
#            MONITOR ACTIVE SESSIONS
# ====================================================

async def admin_monitor_sessions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitor all active sessions"""
    query = update.callback_query
    await query.answer()

    admin = query.from_user
    admin_name = admin.full_name
    admin_username = f"@{admin.username}" if admin.username else None
    admin_id = admin.id

    username_line = f"🆔 *Username:* {admin_username}\n" if admin_username else ""

    if not active_sessions:
        await query.message.reply_text(
            f"❌ *NO ACTIVE SESSIONS*\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"👤 *Admin:* {admin_name}\n"
            f"{username_line}"
            f"🔑 *Admin ID:* `{admin_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"There are currently no active conversations.",
            parse_mode="Markdown"
        )
        return

    message = (
        f"🧵 *ACTIVE SESSIONS MONITOR*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *Admin:* {admin_name}\n"
        f"{username_line}"
        f"🔑 *Admin ID:* `{admin_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🔄 *Live Conversations:*\n\n"
    )

    for user_id, session_info in active_sessions.items():
        seller_id = session_info["seller_id"]
        product = session_info["product"]
        start_time = session_start_times.get(user_id, "Unknown")

        if isinstance(start_time, datetime):
            duration = datetime.now() - start_time
            duration_str = f"{duration.seconds // 60} min"
        else:
            duration_str = "Unknown"

        message += (
            f"👤 *User:* `{user_id}`\n"
            f"💼 *Seller:* `{seller_id}`\n"
            f"📦 *Product:* {product}\n"
            f"⏱️ *Duration:* {duration_str}\n"
            f"━━━━━━━━━━━━━━━━━\n"
        )

    keyboard = []
    for user_id in active_sessions.keys():
        keyboard.append([
            InlineKeyboardButton(f"🛑 Force Stop User {user_id}", callback_data=f"force_stop_{user_id}")
        ])
    keyboard.append([InlineKeyboardButton("« Back", callback_data="admin_back")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

async def force_stop_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force stop a session"""
    query = update.callback_query
    await query.answer()

    try:
        user_id = int(query.data.split('_')[2])
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Invalid session.")
        return

    if user_id not in active_sessions:
        await query.message.reply_text("❌ Session not found.")
        return

    session_info = active_sessions[user_id]
    seller_id = session_info["seller_id"]
    product = session_info["product"]
    start_time = session_start_times.get(user_id, datetime.now())

    log_chat(user_id, seller_id, product, start_time)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Your session was ended by an administrator."
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    try:
        await context.bot.send_message(
            chat_id=seller_id,
            text=f"⚠️ Your session with user {user_id} was ended by an administrator."
        )
    except Exception as e:
        logger.error(f"Failed to notify seller {seller_id}: {e}")

    del active_sessions[user_id]
    del reverse_sessions[seller_id]
    if user_id in session_start_times:
        del session_start_times[user_id]

    await query.message.reply_text(f"✅ Session with user {user_id} force stopped.")

# ====================================================
#            BACK TO ADMIN PANEL
# ====================================================

async def admin_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to admin panel main menu"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔧 Manage Sellers", callback_data="admin_manage_sellers"),
         InlineKeyboardButton("🛍 Manage Products", callback_data="admin_manage_products")],
        [InlineKeyboardButton("📨 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton("📊 Global Statistics", callback_data="admin_global_stats")],
        [InlineKeyboardButton("🧵 Monitor Sessions", callback_data="admin_monitor_sessions"),
         InlineKeyboardButton("📝 Logs", callback_data="admin_logs")],
        [InlineKeyboardButton("📤 Export Data", callback_data="admin_export"),
         InlineKeyboardButton("🚨 Emergency Tools", callback_data="admin_emergency")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="🔧 Admin Panel\n\nChoose an option:",
        reply_markup=reply_markup
    )