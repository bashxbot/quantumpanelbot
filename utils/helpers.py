"""
Helper functions for Quantum Panel Bot
"""

from datetime import datetime
from config import ADMINS, SELLERS, PRODUCT_SELLERS
from utils.data import seller_stats, chat_history

# ====================================================
#                PERMISSION HELPERS
# ====================================================

def is_admin(user_id):
    """Check if user is an admin"""
    return user_id in ADMINS

def is_seller(user_id):
    """Check if user is a seller or admin"""
    return user_id in SELLERS or user_id in ADMINS

# ====================================================
#                STATISTICS HELPERS
# ====================================================

def get_seller_stats(seller_id):
    """Get or initialize seller statistics"""
    if seller_id not in seller_stats:
        seller_stats[seller_id] = {
            "total_served": 0,
            "chats_completed": 0,
            "last_10_users": [],
            "today_stats": 0,
            "monthly_stats": 0
        }
    return seller_stats[seller_id]

def update_seller_stats(seller_id, user_id):
    """Update seller statistics after completing a chat"""
    stats = get_seller_stats(seller_id)
    stats["total_served"] += 1
    stats["chats_completed"] += 1
    stats["today_stats"] += 1
    stats["monthly_stats"] += 1

    if user_id not in stats["last_10_users"]:
        stats["last_10_users"].insert(0, user_id)
        if len(stats["last_10_users"]) > 10:
            stats["last_10_users"] = stats["last_10_users"][:10]

def log_chat(user_id, seller_id, product, start_time, end_time=None):
    """Log a completed chat to history"""
    chat_history.append({
        "user_id": user_id,
        "seller_id": seller_id,
        "product": product,
        "start_time": start_time,
        "end_time": end_time or datetime.now(),
        "messages": 0
    })

# ====================================================
#                PRODUCT HELPERS
# ====================================================

def get_products_for_seller(seller_id):
    """Get all products assigned to a seller"""
    products = []
    for product, sellers in PRODUCT_SELLERS.items():
        if seller_id in sellers:
            products.append(product)
    return products