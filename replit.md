# Quantum Panel Telegram Bot

## Overview
A Telegram bot for managing products and sellers. The bot allows users to browse products, connect with sellers, and enables sellers to manage their inventory and customer chats.

## Current Status
✅ **Bot is running successfully!**
- Connected to Telegram API
- Receiving and responding to user messages
- All handlers and workflows configured

## Project Structure
```
.
├── main.py                    # Main bot entry point
├── config.py                  # Configuration (BOT_TOKEN, admin/seller IDs)
├── handlers/                  # Bot command and callback handlers
│   ├── user_handlers.py      # User-facing commands
│   ├── seller_handlers.py    # Seller panel functions
│   └── admin_handlers.py     # Admin panel functions
├── conversations/             # Conversation flows
│   └── admin_conversations.py
├── utils/                     # Helper functions
│   ├── data.py
│   └── helpers.py
└── attached_assets/          # Images and media files

```

## Recent Changes (Nov 16, 2025)
- ✅ Imported from GitHub repository
- ✅ Fixed package conflicts (removed conflicting `telegram` package)
- ✅ Fixed syntax error in user_handlers.py (f-string backslash issue)
- ✅ Configured bot token in config.py
- ✅ Bot successfully started and running

## Configuration

### Bot Token
**Location:** `config.py` line 13
- The bot token is currently hardcoded in `config.py`
- ⚠️ **SECURITY NOTE:** The bot token should be kept private. Consider moving it to environment variables for production use.

### Admin & Seller IDs
**Location:** `config.py` lines 18-19
- Admins: `[6170236685, 6562270244]`
- Sellers: `[6170236685, 6562270244]`

### Products
Currently configured product:
- **KOS-8BP**: Official KOS 8 Ball Pool key
  - Sellers: [6562270244, 6170236685]
  - Image: KOS.jpg

## Dependencies
- `python-telegram-bot==22.5` - Main Telegram bot framework
- Various supporting packages (httpx, anyio, etc.)

## Running the Bot
The bot runs automatically via the "Telegram Bot" workflow:
- Command: `python main.py`
- Status: ✅ Running
- Logs available in workflow console

## Known Issues
- LSP shows import resolution warnings for `telegram` and `telegram.ext` - these are false positives and don't affect functionality
- ConversationHandler warnings about `per_message=False` - informational only, bot works fine

## User Preferences
- Bot token stored in config.py (as requested by user)
- No environment variables used for secrets

## Important Notes
1. The bot token was shared in chat - this is generally not recommended for security reasons
2. If the bot token is ever compromised, regenerate it via @BotFather on Telegram
3. The .gitignore file is properly configured to exclude common Python artifacts
