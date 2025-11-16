"""
Configuration file for Quantum Panel Bot
Contains all bot settings, constants, and conversation states
"""

import os

# ====================================================
#                BOT TOKEN
# ====================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# ====================================================
#                ADMIN & SELLER IDS
# ====================================================

ADMINS = [6170236685, 6562270244]
SELLERS = [6170236685, 6562270244]

# ====================================================
#                PRODUCT CONFIGURATION
# ====================================================

# Product sellers mapping: product_name -> [seller_id1, seller_id2, ...]
PRODUCT_SELLERS = {
    "KOS-8BP": [6562270244, 6170236685]
}

# Product descriptions
PRODUCT_DESCRIPTIONS = {
    "KOS-8BP": "Official KOS 8 Ball Pool key."
}

# Product images
PRODUCT_IMAGES = {
    "KOS-8BP": "KOS.jpg"
}

# Start image
START_IMAGE = "Quantum.jpg"

# ====================================================
#                CONVERSATION STATES
# ====================================================

(WAITING_SELLER_ID, WAITING_PRODUCT_NAME, WAITING_PRODUCT_DESC, 
 WAITING_PRODUCT_IMAGE, WAITING_PRODUCT_SELLERS, WAITING_EDIT_CHOICE,
 WAITING_BROADCAST_MESSAGE, WAITING_BLOCK_USER_ID, WAITING_UNBLOCK_USER_ID,
 WAITING_REMOVE_SELLER_ID, WAITING_ASSIGN_PRODUCT_SELLERS,
 WAITING_REMOVE_SELLER_FROM_PRODUCT, WAITING_PRODUCT_FOR_SELLER,
 WAITING_VIEW_PRODUCT_SELLERS) = range(14)
