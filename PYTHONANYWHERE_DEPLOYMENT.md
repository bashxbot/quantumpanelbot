# PythonAnywhere Deployment Guide
## Quantum Panel Telegram Bot

This guide will walk you through deploying your Telegram bot to PythonAnywhere.

---

## 📋 Prerequisites

1. **PythonAnywhere Account** - Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
   - Free account works perfectly!
2. **Your Bot Token** - Already configured in `config.py`
3. **Files to Upload** - All the files from this project

---

## 🚀 Step-by-Step Deployment

### Step 1: Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account
3. Verify your email

### Step 2: Upload Your Files

**Option A: Using Git (Recommended)**
1. Open a **Bash console** on PythonAnywhere (from Consoles tab)
2. Clone your repository:
   ```bash
   git clone https://github.com/bashxbot/quantumpanelbot.git
   cd quantumpanelbot
   ```

**Option B: Manual Upload**
1. Go to **Files** tab
2. Create a new directory: `quantumpanelbot`
3. Upload all your project files to this directory

### Step 3: Install Dependencies

1. Open a **Bash console**
2. Navigate to your project:
   ```bash
   cd ~/quantumpanelbot
   ```
3. Install required packages:
   ```bash
   pip3 install --user -r requirements.txt
   ```

### Step 4: Configure the Flask App

1. Open `flask_app.py` in the PythonAnywhere file editor
2. **Find these lines** (around line 80-85):
   ```python
   SECRET_PATH = "quantum_webhook_secure_path_123xyz"  # Change this!
   PYTHONANYWHERE_DOMAIN = "yourusername.pythonanywhere.com"
   ```
3. **Update them:**
   - Change `SECRET_PATH` to a long, random string (for security)
   - Replace `yourusername` with your actual PythonAnywhere username
   
   Example:
   ```python
   SECRET_PATH = "my_super_secret_random_path_987654321"
   PYTHONANYWHERE_DOMAIN = "johnsmith.pythonanywhere.com"
   ```

⚠️ **IMPORTANT SECURITY NOTE:**
- Your bot token is currently stored in `config.py`
- Make sure to keep this file private and never share it publicly
- Consider using PythonAnywhere's environment variables feature for production:
  - In PythonAnywhere: Web tab → Environment variables
  - Add: `BOT_TOKEN` = your token
  - Update `config.py` to use: `BOT_TOKEN = os.getenv("BOT_TOKEN", "your_fallback_token")`

### Step 5: Create Web App

1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (NOT Flask)
4. Select **Python 3.10** (or latest available)
5. Click **Next**

### Step 6: Configure WSGI File

1. In the **Web** tab, scroll to **Code** section
2. Click on the WSGI configuration file link (something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Delete all the existing content**
4. Copy and paste the following (replace `yourusername` with your username):

   ```python
   import sys
   import os

   # Add your project directory
   project_home = '/home/yourusername/quantumpanelbot'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Import the Flask app
   from flask_app import app as application
   ```

5. Click **Save**

### Step 7: Set Working Directory

1. Still in the **Web** tab, scroll to **Code** section
2. Set **Source code** to: `/home/yourusername/quantumpanelbot`
3. Set **Working directory** to: `/home/yourusername/quantumpanelbot`

### Step 8: Reload Web App

1. Scroll to the top of the **Web** tab
2. Click the big green **Reload yourusername.pythonanywhere.com** button
3. Wait for it to finish (you'll see a success message)

### Step 9: Activate the Webhook

1. Open your browser and visit:
   ```
   https://yourusername.pythonanywhere.com/set_webhook
   ```
   (Replace `yourusername` with your actual username)

2. You should see:
   ```
   ✅ Webhook set successfully to: https://yourusername.pythonanywhere.com/your_secret_path
   ```

### Step 10: Test Your Bot! 🎉

1. Open Telegram
2. Go to your bot
3. Send `/start` command
4. Your bot should respond!

---

## 🔍 Troubleshooting

### Bot Not Responding?

**Check Webhook Status:**
Visit: `https://yourusername.pythonanywhere.com/webhook_info`

**Check Error Logs:**
1. Go to **Web** tab on PythonAnywhere
2. Scroll to **Log files**
3. Click on **Error log**
4. Look for any Python errors

**Common Issues:**

1. **404 Error on webhook:**
   - Make sure `SECRET_PATH` in flask_app.py matches
   - Reload your web app

2. **ImportError:**
   - Check that all dependencies are installed: `pip3 install --user -r requirements.txt`
   - Make sure WSGI file has correct path

3. **Webhook not set:**
   - Visit `/set_webhook` URL again
   - Check webhook_info to confirm

4. **Bot token invalid:**
   - Verify `BOT_TOKEN` in `config.py` is correct
   - Get new token from @BotFather if needed

---

## 🛠 Useful URLs

Replace `yourusername` with your actual PythonAnywhere username:

- **Bot Home:** `https://yourusername.pythonanywhere.com/`
- **Set Webhook:** `https://yourusername.pythonanywhere.com/set_webhook`
- **Check Webhook:** `https://yourusername.pythonanywhere.com/webhook_info`
- **Delete Webhook:** `https://yourusername.pythonanywhere.com/delete_webhook`

---

## 📝 Important Notes

### Security
- ✅ Your `SECRET_PATH` should be long and random
- ✅ Never share your webhook URL publicly
- ✅ Keep your bot token private

### Free Account Limitations
- Your web app will sleep after inactivity
- Visit your URL daily to keep it active
- Consider upgrading to paid account for 24/7 uptime

### Updates
After making code changes:
1. Upload new files to PythonAnywhere
2. Go to **Web** tab
3. Click **Reload** button

---

## 🎯 Quick Reference

### File Structure on PythonAnywhere
```
/home/yourusername/quantumpanelbot/
├── flask_app.py           # Main Flask application
├── config.py              # Bot configuration
├── main.py                # Original polling version (not used)
├── handlers/              # Bot handlers
├── conversations/         # Conversation flows
├── utils/                 # Helper functions
├── attached_assets/       # Images
└── requirements.txt       # Dependencies
```

### Important Commands

**Install dependencies:**
```bash
cd ~/quantumpanelbot
pip3 install --user -r requirements.txt
```

**Update from Git:**
```bash
cd ~/quantumpanelbot
git pull origin main
```

**Check installed packages:**
```bash
pip3 list --user
```

---

## ✅ Deployment Checklist

- [ ] PythonAnywhere account created
- [ ] Files uploaded to `/home/yourusername/quantumpanelbot/`
- [ ] Dependencies installed via `pip3 install --user -r requirements.txt`
- [ ] `flask_app.py` updated with correct SECRET_PATH and domain
- [ ] WSGI file configured
- [ ] Web app created and configured
- [ ] Web app reloaded
- [ ] Webhook activated via `/set_webhook`
- [ ] Bot tested in Telegram
- [ ] Bot responding to commands ✅

---

## 🎉 Success!

Your Quantum Panel Bot is now running 24/7 on PythonAnywhere!

**Need Help?**
- Check the error logs on PythonAnywhere
- Visit webhook_info to see webhook status
- Make sure all configuration is correct

**Happy Botting! 🤖**
