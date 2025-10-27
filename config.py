# config.py

import os

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7914051771:AAHBSJxb4QJ2o4TiSNL0P-bHyEeTkYsD6Eo")

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://bunkrindian:starzplay@cluster0.xart63p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "telegram_bot_db"

# API Keys
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "your_pollinations_api_key")
PIXVID_API_KEY = os.environ.get("PIXVID_API_KEY", "f2aee9480da2c75211f143f4a308bff0c83b2990b72cf21794f207591db93a39")

# Bot Owner ID
OWNER_ID = int(os.environ.get("OWNER_ID", 6449644059))

# Session Timeout (in seconds)
SESSION_TIMEOUT = 3600  # 1 hour

# Daily Claim Configuration
MIN_CLAIM_AMOUNT = int(os.environ.get("MIN_CLAIM_AMOUNT", 50))
MAX_CLAIM_AMOUNT = int(os.environ.get("MAX_CLAIM_AMOUNT", 200))

# AI Model Configuration
NORMAL_MODEL = "openai"
INTIMATE_MODEL = "mistral"
