"""
User flow handlers for Quantum Panel Bot
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import (
    START_IMAGE, PRODUCT_IMAGES, PRODUCT_DESCRIPTIONS,
    PRODUCT_SELLERS, ADMINS, SELLERS
)
from utils import (
    active_sessions, reverse_sessions, pending_requests,
    user_product_selection, seller_alerts, all_users,
    blocked_users, buy_button_enabled, session_start_times,
    update_seller_stats, log_chat
)

logger = logging.getLogger(__name__)

# ====================================================
#                    START COMMAND
# ====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - send image with welcome message"""
    user_id = update.message.from_user.id
    user = update.message.from_user
    user_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"
    all_users.add(user_id)

    # Check if user is in an active session
    if user_id in active_sessions or user_id in reverse_sessions:
        await update.message.reply_text(
            f"⚠️ *Active Session Detected*\n\n"
            f"👤 {user_name} ({username})\n"
            f"Please use /stop to end the current conversation before using other commands.",
            parse_mode="Markdown"
        )
        return

    if user_id in blocked_users:
        await update.message.reply_text(
            f"⛔ *ACCESS DENIED*\n\n"
            f"You have been blocked from using this bot.\n\n"
            f"👤 {user_name} ({username})",
            parse_mode="Markdown"
        )
        return

    # Check if user is admin or seller
    if user_id in ADMINS:
        keyboard = [
            [InlineKeyboardButton("🔧 Admin Panel", callback_data="open_admin_panel"),
             InlineKeyboardButton("💼 Seller Panel", callback_data="open_seller_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        admin_message = (
            f"✨ *Welcome Back, Admin!* ✨\n\n"
            f"👤 *Name:* {user_name}\n"
            f"🆔 *Username:* {username}\n"
            f"🔑 *User ID:* `{user_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🎯 Choose your control panel below:"
        )

        try:
            with open(START_IMAGE, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=admin_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
        except FileNotFoundError:
            logger.warning(f"Start image not found: {START_IMAGE}")
            await update.message.reply_text(admin_message, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send start image: {e}")
            await update.message.reply_text(admin_message, reply_markup=reply_markup, parse_mode="Markdown")
        return
    elif user_id in SELLERS:
        keyboard = [
            [InlineKeyboardButton("💼 Seller Panel", callback_data="open_seller_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        seller_message = (
            f"🎉 *Welcome, Seller!* 🎉\n\n"
            f"👤 *Name:* {user_name}\n"
            f"🆔 *Username:* {username}\n"
            f"🔑 *User ID:* `{user_id}`\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"💼 Access your seller panel below:"
        )

        try:
            with open(START_IMAGE, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=seller_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
        except FileNotFoundError:
            logger.warning(f"Start image not found: {START_IMAGE}")
            await update.message.reply_text(seller_message, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send start image: {e}")
            await update.message.reply_text(seller_message, reply_markup=reply_markup, parse_mode="Markdown")
        return

    keyboard = [
        [InlineKeyboardButton("🔑 Buy Key(s)", callback_data="buy_keys")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        f"🌟 *Welcome to Quantum Panel!* 🌟\n\n"
        f"👤 *Name:* {user_name}\n"
        f"🆔 *Username:* {username}\n"
        f"🔑 *User ID:* `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🛒 This bot helps you buy *official keys* directly from our authorized sellers.\n\n"
        f"✨ Please choose an option below to get started!"
    )

    try:
        with open(START_IMAGE, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except FileNotFoundError:
        logger.warning(f"Start image not found: {START_IMAGE}")
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send start image: {e}")
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

# ====================================================
#            PRODUCT SELECTION MENU
# ====================================================

async def buy_keys_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Buy Keys button press - show product selection menu"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = query.from_user
    user_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"

    if user_id in blocked_users:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"⛔ *ACCESS BLOCKED*\n\n"
                f"You have been blocked from using this bot.\n\n"
                f"👤 {user_name} ({username})"
            ),
            parse_mode="Markdown"
        )
        return

    if not buy_button_enabled:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🚫 *Service Temporarily Unavailable*\n\n"
                f"The buy feature is currently disabled.\n"
                f"Please try again later.\n\n"
                f"👤 {user_name} ({username})"
            ),
            parse_mode="Markdown"
        )
        return

    if user_id in active_sessions:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ *Already Connected!*\n\n"
                f"You are already in an active conversation with a seller.\n"
                f"💬 Send your message directly.\n\n"
                f"👤 {user_name} ({username})"
            ),
            parse_mode="Markdown"
        )
        return

    if user_id in pending_requests:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"⏳ *Request Pending*\n\n"
                f"You already have a pending connection request.\n"
                f"⏰ Please wait for a seller to accept.\n\n"
                f"👤 {user_name} ({username})"
            ),
            parse_mode="Markdown"
        )
        return

    keyboard = []
    for product_name in PRODUCT_SELLERS.keys():
        keyboard.append([InlineKeyboardButton(f"🎯 {product_name}", callback_data=f"product_{product_name}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"🛍️ *Product Selection Menu*\n\n"
            f"👤 {user_name} ({username})\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📦 Please choose a product from the list below:"
        ),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ====================================================
#        PRODUCT IMAGE + CONNECT STEP
# ====================================================

async def product_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection - show product image and connect button"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = query.from_user
    user_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"

    try:
        product_name = query.data.split('_', 1)[1]
    except (IndexError, ValueError):
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ *Invalid Selection*\n\n👤 {user_name} ({username})",
            parse_mode="Markdown"
        )
        return

    if product_name not in PRODUCT_SELLERS:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ *Invalid Product*\n\n👤 {user_name} ({username})",
            parse_mode="Markdown"
        )
        return

    if not PRODUCT_SELLERS[product_name]:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ *Product Unavailable*\n\n"
                f"Sorry, this product is currently unavailable.\n\n"
                f"👤 {user_name} ({username})"
            ),
            parse_mode="Markdown"
        )
        return

    user_product_selection[user_id] = product_name
    description = PRODUCT_DESCRIPTIONS.get(product_name, "No description available.")

    keyboard = [
        [InlineKeyboardButton("🔗 Connect with Seller", callback_data=f"connect_{product_name}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    product_message = (
        f"📦 *Product Details*\n\n"
        f"🎯 *Product:* {product_name}\n"
        f"📝 *Description:* {description}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *Customer:* {user_name}\n"
        f"🆔 *Username:* {username}\n\n"
        f"✨ Click below to connect with a seller!"
    )

    await query.message.delete()

    if product_name in PRODUCT_IMAGES:
        try:
            with open(PRODUCT_IMAGES[product_name], 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=product_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
        except FileNotFoundError:
            logger.warning(f"Product image not found: {PRODUCT_IMAGES[product_name]}")
            await context.bot.send_message(chat_id=user_id, text=product_message, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send product image: {e}")
            await context.bot.send_message(chat_id=user_id, text=product_message, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=user_id, text=product_message, reply_markup=reply_markup, parse_mode="Markdown")

# ====================================================
#            CONNECTION REQUEST SYSTEM
# ====================================================

async def connect_with_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Connect with Seller button - send request to product-specific sellers"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id
    user_full_name = user.full_name
    username = f"@{user.username}" if user.username else "No username"

    try:
        product_name = query.data.split('_', 1)[1]
    except (IndexError, ValueError):
        await query.message.reply_text(
            f"❌ *Invalid Request*\n\n👤 {user_full_name} ({username})",
            parse_mode="Markdown"
        )
        return

    if product_name not in PRODUCT_SELLERS or not PRODUCT_SELLERS[product_name]:
        await query.message.reply_text(
            f"❌ *Product Unavailable*\n\nSorry, this product is currently unavailable.\n\n👤 {user_full_name} ({username})",
            parse_mode="Markdown"
        )
        return

    if user_id in active_sessions:
        await query.message.reply_text(
            f"✅ *Already Connected!*\nYou are already connected to a seller.\n💬 Send your message directly.\n\n👤 {user_full_name} ({username})",
            parse_mode="Markdown"
        )
        return

    if user_id in pending_requests:
        await query.message.reply_text(
            f"⏳ *Request Pending*\n\nYou already have a pending request.\n⏰ Please wait for a seller to accept.\n\n👤 {user_full_name} ({username})",
            parse_mode="Markdown"
        )
        return

    await query.message.delete()
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"⏳ *Connection Request Sent!*\n\n"
            f"📦 Product: *{product_name}*\n"
            f"👤 Customer: {user_full_name}\n"
            f"🆔 Username: {username}\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🔔 Your request has been sent to authorized sellers.\n"
            f"⏰ Please wait for someone to accept..."
        ),
        parse_mode="Markdown"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Accept Request", callback_data=f"accept_{user_id}_{product_name}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    request_message = (
        f"🆕 *NEW CONNECTION REQUEST*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📦 *Product:* {product_name}\n"
        f"👤 *Customer:* {user_full_name}\n"
        f"🆔 *Username:* {username}\n"
        f"🔑 *User ID:* `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✨ Click *\"Accept\"* to take this customer!"
    )

    product_sellers = PRODUCT_SELLERS[product_name]

    for seller_id in product_sellers:
        if seller_alerts.get(seller_id, True):
            try:
                await context.bot.send_message(
                    chat_id=seller_id,
                    text=request_message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to send request to seller {seller_id}: {e}")

    pending_requests[user_id] = {"product": product_name}

# ====================================================
#            ACCEPT REQUEST
# ====================================================

async def accept_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Accept Request button press - ONLY ADMINS CAN ACCEPT"""
    query = update.callback_query
    acceptor_id = query.from_user.id
    acceptor = query.from_user
    acceptor_name = acceptor.full_name
    acceptor_username = f"@{acceptor.username}" if acceptor.username else "No username"

    try:
        parts = query.data.split('_')
        user_id = int(parts[1])
        product_name = parts[2]
    except (IndexError, ValueError):
        await query.answer("❌ Invalid request.", show_alert=True)
        return

    if acceptor_id not in ADMINS:
        await query.answer("❌ You are not allowed to accept requests.", show_alert=True)
        return

    if user_id not in pending_requests:
        await query.answer("❌ This request is no longer active.", show_alert=True)
        return

    if user_id in active_sessions:
        await query.answer("❌ Another seller has already accepted this request.", show_alert=True)
        return

    active_sessions[user_id] = {"seller_id": acceptor_id, "product": product_name}
    reverse_sessions[acceptor_id] = user_id
    session_start_times[user_id] = datetime.now()

    del pending_requests[user_id]

    if user_id in user_product_selection:
        del user_product_selection[user_id]

    await query.answer("✅ Request accepted!", show_alert=True)

    try:
        user = await context.bot.get_chat(user_id)
        user_full_name = user.full_name
        user_username = f"@{user.username}" if user.username else "No username"
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        user_full_name = "Unknown User"
        user_username = "No username"

    customer_username_line = f"  • Username: {user_username}\n" if user_username != "No username" else ""

    await query.message.reply_text(
        f"📞 *CONNECTION STARTED*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📦 *Product:* {product_name}\n\n"
        f"👤 *Customer Details:*\n"
        f"  • Name: {user_full_name}\n"
        f"{customer_username_line}"
        f"  • ID: `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💬 You are now connected!\n"
        f"📝 Send messages normally.\n"
        f"🛑 Use /stop to end the conversation.",
        parse_mode="Markdown"
    )

    seller_username_line = f"  • Username: {acceptor_username}\n" if acceptor_username != "No username" else ""

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ *CONNECTION SUCCESSFUL!*\n\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"💼 *Connected Seller:*\n"
                f"  • Name: {acceptor_name}\n"
                f"{seller_username_line}"
                f"  • ID: `{acceptor_id}`\n\n"
                f"📦 *Product:* {product_name}\n\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"💬 Start your conversation below..."
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

# ====================================================
#        ACTIVE CONVERSATION ROUTING
# ====================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route messages between users and assigned admins only"""
    if not update.message or not update.message.text:
        return

    sender_id = update.message.from_user.id
    sender = update.message.from_user
    sender_name = sender.full_name
    sender_username = f"@{sender.username}" if sender.username else "No username"
    message_text = update.message.text

    if sender_id in active_sessions:
        session_info = active_sessions[sender_id]
        seller_id = session_info["seller_id"]
        product = session_info["product"]

        try:
            await context.bot.send_message(
                chat_id=seller_id,
                text=(
                    f"💬 *Message from Customer*\n\n"
                    f"👤 {sender_name} ({sender_username})\n"
                    f"🔑 ID: `{sender_id}`\n"
                    f"📦 Product: {product}\n\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{message_text}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to forward message to seller {seller_id}: {e}")
            await update.message.reply_text(
                f"❌ *Failed to Send Message*\n\nThe seller may have blocked the bot.\n\n👤 {sender_name} ({sender_username})",
                parse_mode="Markdown"
            )

    elif sender_id in reverse_sessions:
        user_id = reverse_sessions[sender_id]
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"💼 *Message from Seller*\n\n"
                    f"👤 {sender_name} ({sender_username})\n\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"{message_text}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to forward message to user {user_id}: {e}")
            await update.message.reply_text(
                f"❌ *Failed to Send Message*\n\nThe user may have blocked the bot.\n\n👤 {sender_name} ({sender_username})",
                parse_mode="Markdown"
            )

# ====================================================
#                    STOP COMMAND
# ====================================================

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command - only assigned seller can stop conversation"""
    seller_id = update.message.from_user.id
    seller = update.message.from_user
    seller_name = seller.full_name
    seller_username = f"@{seller.username}" if seller.username else "No username"

    if seller_id not in reverse_sessions:
        await update.message.reply_text(
            f"❌ *No Active Session*\n\nYou don't have an active conversation to stop.\n\n👤 {seller_name} ({seller_username})",
            parse_mode="Markdown"
        )
        return

    user_id = reverse_sessions[seller_id]
    session_info = active_sessions[user_id]
    product = session_info["product"]
    start_time = session_start_times.get(user_id, datetime.now())

    update_seller_stats(seller_id, user_id)
    log_chat(user_id, seller_id, product, start_time)

    try:
        user = await context.bot.get_chat(user_id)
        user_name = user.full_name
        user_username = f"@{user.username}" if user.username else "No username"
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        user_name = "Unknown User"
        user_username = "No username"

    user_username_line = f"  • Username: {user_username}\n" if user_username != "No username" else ""

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"⚠️ *CONVERSATION ENDED*\n\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"The seller has ended the conversation.\n\n"
                f"👤 Your Details:\n"
                f"  • Name: {user_name}\n"
                f"{user_username_line}"
                f"━━━━━━━━━━━━━━━━━\n"
                f"💡 If you still need help, tap *Buy Key(s)* again!"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    customer_username_line = f"  • Username: {user_username}\n" if user_username != "No username" else ""

    await update.message.reply_text(
        f"🛑 *CONVERSATION STOPPED*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📦 *Product:* {product}\n\n"
        f"👤 *Customer:*\n"
        f"  • Name: {user_name}\n"
        f"{customer_username_line}"
        f"  • ID: `{user_id}`\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ Session ended successfully!",
        parse_mode="Markdown"
    )

    del reverse_sessions[seller_id]
    del active_sessions[user_id]
    if user_id in session_start_times:
        del session_start_times[user_id]