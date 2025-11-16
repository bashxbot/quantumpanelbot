"""
Admin conversation handlers for Quantum Panel Bot
Handles multi-step interactions for admin operations
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import (
    ADMINS, SELLERS, PRODUCT_SELLERS, PRODUCT_DESCRIPTIONS, PRODUCT_IMAGES,
    WAITING_SELLER_ID, WAITING_REMOVE_SELLER_ID, WAITING_PRODUCT_NAME,
    WAITING_PRODUCT_DESC, WAITING_PRODUCT_IMAGE, WAITING_PRODUCT_SELLERS,
    WAITING_ASSIGN_PRODUCT_SELLERS, WAITING_REMOVE_SELLER_FROM_PRODUCT,
    WAITING_BROADCAST_MESSAGE, WAITING_BLOCK_USER_ID, WAITING_UNBLOCK_USER_ID
)
from utils.data import temp_data, all_users, blocked_users

logger = logging.getLogger(__name__)

# ====================================================
#            ADD SELLER CONVERSATION
# ====================================================

async def admin_add_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add seller conversation - after product selection"""
    query = update.callback_query
    await query.answer()
    
    try:
        product_name = query.data.split('_', 2)[2]
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Invalid product.")
        return ConversationHandler.END
    
    temp_data[query.from_user.id] = {"product_for_seller": product_name}
    
    await query.message.reply_text(
        f"➕ Add Seller to '{product_name}'\n\n"
        "Please send the Telegram User ID of the seller to add.\n"
        "Use /cancel to abort."
    )
    return WAITING_SELLER_ID

async def receive_seller_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and process seller ID"""
    user_id = update.message.from_user.id
    
    try:
        seller_id = int(update.message.text.strip())
        product_name = temp_data[user_id]["product_for_seller"]
        
        if seller_id not in SELLERS:
            SELLERS.append(seller_id)
        
        if product_name in PRODUCT_SELLERS:
            if seller_id in PRODUCT_SELLERS[product_name]:
                await update.message.reply_text(f"❌ Seller {seller_id} is already assigned to '{product_name}'.")
            else:
                PRODUCT_SELLERS[product_name].append(seller_id)
                await update.message.reply_text(f"✅ Seller {seller_id} added to '{product_name}' successfully!")
        else:
            await update.message.reply_text("❌ Product not found.")
        
        del temp_data[user_id]
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Please enter a numeric user ID.")
    
    return ConversationHandler.END

# ====================================================
#            REMOVE SELLER CONVERSATION
# ====================================================

async def admin_remove_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start remove seller conversation - after product selection"""
    query = update.callback_query
    await query.answer()
    
    try:
        product_name = query.data.split('_', 2)[2]
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Invalid product.")
        return ConversationHandler.END
    
    if product_name not in PRODUCT_SELLERS or not PRODUCT_SELLERS[product_name]:
        await query.message.reply_text(f"❌ No sellers assigned to '{product_name}'.")
        return ConversationHandler.END
    
    temp_data[query.from_user.id] = {"product_for_seller": product_name}
    
    # Fetch seller details
    seller_list = []
    for sid in PRODUCT_SELLERS[product_name]:
        try:
            seller_chat = await context.bot.get_chat(sid)
            seller_name = seller_chat.full_name or "Unknown"
            seller_username = f"@{seller_chat.username}" if seller_chat.username else ""
            seller_info = f"• {seller_name}"
            if seller_username:
                seller_info += f" {seller_username}"
            seller_info += f" (ID: `{sid}`)"
            seller_list.append(seller_info)
        except Exception as e:
            logger.error(f"Failed to fetch seller {sid}: {e}")
            seller_list.append(f"• ID: `{sid}`")
    
    sellers_text = "\n".join(seller_list)
    await query.message.reply_text(
        f"➖ *Remove Seller from '{product_name}'*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👥 *Current Sellers:*\n{sellers_text}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"Please send the Seller ID to remove.\n"
        f"Use /cancel to abort.",
        parse_mode="Markdown"
    )
    return WAITING_REMOVE_SELLER_ID

async def receive_remove_seller_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and remove seller ID"""
    user_id = update.message.from_user.id
    
    try:
        seller_id = int(update.message.text.strip())
        product_name = temp_data[user_id]["product_for_seller"]
        
        if product_name in PRODUCT_SELLERS and seller_id in PRODUCT_SELLERS[product_name]:
            PRODUCT_SELLERS[product_name].remove(seller_id)
            await update.message.reply_text(f"✅ Seller {seller_id} removed from '{product_name}' successfully.")
        else:
            await update.message.reply_text("❌ Seller not found in this product.")
        
        del temp_data[user_id]
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")
    
    return ConversationHandler.END

# ====================================================
#            ADD PRODUCT CONVERSATION
# ====================================================

async def admin_add_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add product conversation"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "➕ Add New Product\n\n"
        "Step 1/4: Enter the Product Name.\n"
        "Use /cancel to abort."
    )
    return WAITING_PRODUCT_NAME

async def receive_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive product name"""
    product_name = update.message.text.strip()
    
    if product_name in PRODUCT_SELLERS:
        await update.message.reply_text("❌ Product already exists.")
        return ConversationHandler.END
    
    temp_data[update.message.from_user.id] = {"product_name": product_name}
    await update.message.reply_text("Step 2/4: Enter Product Description.")
    return WAITING_PRODUCT_DESC

async def receive_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive product description"""
    user_id = update.message.from_user.id
    description = update.message.text.strip()
    
    temp_data[user_id]["description"] = description
    await update.message.reply_text("Step 3/4: Send the Product Image.")
    return WAITING_PRODUCT_IMAGE

async def receive_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive product image"""
    user_id = update.message.from_user.id
    
    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        temp_data[user_id]["image"] = file_id
        
        await update.message.reply_text(
            "Step 4/4: Send the Seller IDs for this product, separated by commas.\n"
            "Example: 12345, 67890"
        )
        return WAITING_PRODUCT_SELLERS
    else:
        await update.message.reply_text("❌ Please send an image.")
        return WAITING_PRODUCT_IMAGE

async def receive_product_sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and create product with sellers"""
    user_id = update.message.from_user.id
    seller_ids_text = update.message.text.strip()
    
    try:
        seller_ids = [int(sid.strip()) for sid in seller_ids_text.split(',')]
        
        product_name = temp_data[user_id]["product_name"]
        description = temp_data[user_id]["description"]
        image = temp_data[user_id]["image"]
        
        PRODUCT_SELLERS[product_name] = seller_ids
        PRODUCT_DESCRIPTIONS[product_name] = description
        PRODUCT_IMAGES[product_name] = image
        
        del temp_data[user_id]
        
        await update.message.reply_text(
            f"✅ Product '{product_name}' added successfully!\n"
            f"Assigned sellers: {', '.join(map(str, seller_ids))}"
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid seller IDs. Please use numbers separated by commas.")
        return WAITING_PRODUCT_SELLERS
    
    return ConversationHandler.END

# ====================================================
#            ASSIGN SELLERS TO PRODUCT
# ====================================================

async def select_product_assign_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select product to assign sellers to"""
    query = update.callback_query
    await query.answer()
    
    try:
        product_name = query.data.split('_', 2)[2]
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Invalid product.")
        return ConversationHandler.END
    
    temp_data[query.from_user.id] = {"assign_product": product_name}
    
    await query.message.reply_text(
        f"Send the Seller IDs to assign to '{product_name}', separated by commas.\n"
        "Example: 12345, 67890"
    )
    return WAITING_ASSIGN_PRODUCT_SELLERS

async def receive_assign_sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and assign sellers to product"""
    user_id = update.message.from_user.id
    seller_ids_text = update.message.text.strip()
    
    try:
        seller_ids = [int(sid.strip()) for sid in seller_ids_text.split(',')]
        product_name = temp_data[user_id]["assign_product"]
        
        if product_name in PRODUCT_SELLERS:
            PRODUCT_SELLERS[product_name].extend(seller_ids)
            PRODUCT_SELLERS[product_name] = list(set(PRODUCT_SELLERS[product_name]))
            
            del temp_data[user_id]
            
            await update.message.reply_text(
                f"✅ Sellers assigned to '{product_name}' successfully!\n"
                f"Current sellers: {', '.join(map(str, PRODUCT_SELLERS[product_name]))}"
            )
        else:
            await update.message.reply_text("❌ Product not found.")
    except ValueError:
        await update.message.reply_text("❌ Invalid seller IDs.")
    
    return ConversationHandler.END

# ====================================================
#            REMOVE SELLER FROM PRODUCT
# ====================================================

async def select_product_remove_seller_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select product to remove seller from"""
    query = update.callback_query
    await query.answer()
    
    try:
        product_name = query.data.split('_', 2)[2]
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Invalid product.")
        return ConversationHandler.END
    
    if product_name not in PRODUCT_SELLERS or not PRODUCT_SELLERS[product_name]:
        await query.message.reply_text("❌ No sellers assigned to this product.")
        return ConversationHandler.END
    
    temp_data[query.from_user.id] = {"remove_from_product": product_name}
    
    # Fetch seller details
    seller_list = []
    for sid in PRODUCT_SELLERS[product_name]:
        try:
            seller_chat = await context.bot.get_chat(sid)
            seller_name = seller_chat.full_name or "Unknown"
            seller_username = f"@{seller_chat.username}" if seller_chat.username else ""
            seller_info = f"• {seller_name}"
            if seller_username:
                seller_info += f" {seller_username}"
            seller_info += f" (ID: `{sid}`)"
            seller_list.append(seller_info)
        except Exception as e:
            logger.error(f"Failed to fetch seller {sid}: {e}")
            seller_list.append(f"• ID: `{sid}`")
    
    sellers_text = "\n".join(seller_list)
    await query.message.reply_text(
        f"➖ *Remove Seller from '{product_name}'*\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👥 *Current Sellers:*\n{sellers_text}\n\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"Send the Seller ID to remove:",
        parse_mode="Markdown"
    )
    return WAITING_REMOVE_SELLER_FROM_PRODUCT

async def receive_remove_seller_from_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and remove seller from product"""
    user_id = update.message.from_user.id
    
    try:
        seller_id = int(update.message.text.strip())
        product_name = temp_data[user_id]["remove_from_product"]
        
        if product_name in PRODUCT_SELLERS and seller_id in PRODUCT_SELLERS[product_name]:
            PRODUCT_SELLERS[product_name].remove(seller_id)
            del temp_data[user_id]
            
            await update.message.reply_text(
                f"✅ Seller {seller_id} removed from '{product_name}' successfully."
            )
        else:
            await update.message.reply_text("❌ Seller not found in this product.")
    except ValueError:
        await update.message.reply_text("❌ Invalid seller ID.")
    
    return ConversationHandler.END

# ====================================================
#            BROADCAST CONVERSATIONS
# ====================================================

async def broadcast_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast to users"""
    query = update.callback_query
    await query.answer()
    
    temp_data[query.from_user.id] = {"broadcast_target": "users"}
    await query.message.reply_text(
        "📢 Broadcast to All Users\n\n"
        "Send the message you want to broadcast to all users.\n"
        "You can send text or a photo with caption.\n"
        "Use /cancel to abort."
    )
    return WAITING_BROADCAST_MESSAGE

async def broadcast_sellers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast to sellers"""
    query = update.callback_query
    await query.answer()
    
    temp_data[query.from_user.id] = {"broadcast_target": "sellers"}
    await query.message.reply_text(
        "📢 Broadcast to All Sellers\n\n"
        "Send the message you want to broadcast to all sellers.\n"
        "You can send text or a photo with caption.\n"
        "Use /cancel to abort."
    )
    return WAITING_BROADCAST_MESSAGE

async def broadcast_everyone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast to everyone"""
    query = update.callback_query
    await query.answer()
    
    temp_data[query.from_user.id] = {"broadcast_target": "everyone"}
    await query.message.reply_text(
        "📢 Broadcast to Everyone\n\n"
        "Send the message you want to broadcast to everyone.\n"
        "You can send text or a photo with caption.\n"
        "Use /cancel to abort."
    )
    return WAITING_BROADCAST_MESSAGE

async def receive_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and send broadcast message"""
    user_id = update.message.from_user.id
    target = temp_data[user_id]["broadcast_target"]
    
    # Determine recipients
    recipients = []
    if target == "users":
        recipients = list(all_users - set(SELLERS) - set(ADMINS))
    elif target == "sellers":
        recipients = list(set(SELLERS + ADMINS))
    else:  # everyone
        recipients = list(all_users | set(SELLERS) | set(ADMINS))
    
    success_count = 0
    fail_count = 0
    
    # Send broadcast
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        
        for recipient_id in recipients:
            try:
                await context.bot.send_photo(chat_id=recipient_id, photo=photo, caption=caption)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {recipient_id}: {e}")
                fail_count += 1
    else:
        message_text = update.message.text
        
        for recipient_id in recipients:
            try:
                await context.bot.send_message(chat_id=recipient_id, text=message_text)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {recipient_id}: {e}")
                fail_count += 1
    
    del temp_data[user_id]
    
    await update.message.reply_text(
        f"✅ Broadcast completed!\n"
        f"Sent: {success_count}\n"
        f"Failed: {fail_count}"
    )
    
    return ConversationHandler.END

# ====================================================
#            BLOCK USER CONVERSATION
# ====================================================

async def emergency_block_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start block user conversation"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        "🚫 Block User\n\n"
        "Send the User ID to block.\n"
        "Use /cancel to abort."
    )
    return WAITING_BLOCK_USER_ID

async def receive_block_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and block user"""
    try:
        user_id = int(update.message.text.strip())
        
        if user_id in ADMINS:
            await update.message.reply_text("❌ Cannot block an admin.")
        elif user_id in blocked_users:
            await update.message.reply_text("❌ User is already blocked.")
        else:
            blocked_users.add(user_id)
            await update.message.reply_text(f"✅ User {user_id} has been blocked.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
    
    return ConversationHandler.END

# ====================================================
#            UNBLOCK USER CONVERSATION
# ====================================================

async def emergency_unblock_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start unblock user conversation"""
    query = update.callback_query
    await query.answer()
    
    if not blocked_users:
        await query.message.reply_text("❌ No blocked users.")
        return ConversationHandler.END
    
    blocked_list = "\n".join([f"• {uid}" for uid in blocked_users])
    await query.message.reply_text(
        f"↩️ Unblock User\n\n"
        f"Blocked users:\n{blocked_list}\n\n"
        f"Send the User ID to unblock.\n"
        f"Use /cancel to abort."
    )
    return WAITING_UNBLOCK_USER_ID

async def receive_unblock_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and unblock user"""
    try:
        user_id = int(update.message.text.strip())
        
        if user_id in blocked_users:
            blocked_users.remove(user_id)
            await update.message.reply_text(f"✅ User {user_id} has been unblocked.")
        else:
            await update.message.reply_text("❌ User is not blocked.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
    
    return ConversationHandler.END

# ====================================================
#            CANCEL CONVERSATION
# ====================================================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any ongoing conversation"""
    user_id = update.message.from_user.id
    
    if user_id in temp_data:
        del temp_data[user_id]
    
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END
