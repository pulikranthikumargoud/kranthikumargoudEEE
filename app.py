# -*- coding: utf-8 -*-
"""
A secure and robust Telegram bot that uses the OpenRouter API for chat completions.
This bot is designed for webhook deployment on services like Render.
"""

import os
import sys
import logging
import requests
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Basic Logging Setup ---
# This helps in debugging by showing events and errors in your service logs.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)


# --- Securely Load Configuration from Environment Variables ---
# 🔑 Your secrets must be set in your hosting environment (e.g., Render).
try:
    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
    WEBHOOK_URL = os.environ["RENDER_EXTERNAL_URL"] # Render provides this automatically
except KeyError as e:
    LOGGER.critical(f"❌ FATAL ERROR: Environment variable not found: {e}")
    sys.exit(1)


# --- Bot Configuration & Constants ---
WELCOME_MESSAGE = (
    "👋 Welcome! I am an AI assistant. Ask me anything!\n\n"
    "For more updates, join @kranthikumargoudEEE."
)
USER_DATA_FILE = "users.txt"


# --- Helper Function: Store User Info ---
def store_user(chat_id: int, username: str, first_name: str):
    """Appends a new user's information to a text file."""
    try:
        # 'a+' mode creates the file if it doesn't exist.
        with open(USER_DATA_FILE, "a+") as f:
            f.seek(0) # Go to the start of the file to check if user exists
            if str(chat_id) not in f.read():
                f.write(f"{chat_id},{username},{first_name}\n")
                LOGGER.info(f"✅ New user stored: {first_name} (@{username})")
    except IOError as e:
        LOGGER.error(f"⚠️ Could not write to {USER_DATA_FILE}: {e}")


# --- Command Handler: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, stores the user, and sends a welcome message."""
    user = update.effective_user
    if user:
        store_user(user.id, user.username or "N/A", user.first_name or "N/A")
        await update.message.reply_text(WELCOME_MESSAGE)


# --- Message Handler: Manages AI Chat Logic ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes user messages, gets a response from OpenRouter, and replies."""
    user_input = update.message.text
    chat_id = update.effective_chat.id
    
    # Ensure user is stored if they start by just chatting
    user = update.effective_user
    if user:
        store_user(user.id, user.username or "N/A", user.first_name or "N/A")

    try:
        # Let the user know the bot is working
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # Make the API call to OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-chat-v3.1",  # <-- UPDATED to your chosen model
                "messages": [{"role": "user", "content": user_input}],
            },
            timeout=30  # Wait a maximum of 30 seconds for a response
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Extract the reply from the JSON response
        if data.get("choices") and data["choices"][0].get("message"):
            reply = data["choices"][0]["message"]["content"]
        else:
            LOGGER.error(f"API response missing 'choices' structure: {data}")
            reply = "Sorry, I received an unexpected response from the AI. Please try again."

    except requests.exceptions.Timeout:
        LOGGER.warning("API request timed out.")
        reply = "Sorry, the request took too long. Please try again."
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Network error during API call: {e}")
        reply = "I'm having trouble connecting to the AI service right now. Please check back later."
    except Exception as e:
        LOGGER.critical(f"An unexpected error occurred in chat handler: {e}")
        reply = "An unexpected error occurred. I've notified my developer."

    await update.message.reply_text(reply)


# --- Main Application Setup ---
def main() -> None:
    """Sets up and runs the Telegram bot."""
    LOGGER.info("🚀 Starting bot...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Get port from environment or default to 10000 for Render
    port = int(os.environ.get("PORT", 10000))

    # Configure and run the webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )
    LOGGER.info(f"✅ Bot is live and listening on port {port}")

if __name__ == "__main__":
    main()
