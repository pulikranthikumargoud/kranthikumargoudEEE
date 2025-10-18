# -*- coding: utf-8 -*-
"""
A secure and robust Telegram bot with conversation memory that uses the OpenRouter API.
"""

import os
import sys
import logging
import requests
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Basic Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)


# --- Securely Load Configuration from Environment Variables ---
try:
    TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
    WEBHOOK_URL = os.environ["RENDER_EXTERNAL_URL"]
except KeyError as e:
    LOGGER.critical(f"❌ FATAL ERROR: Environment variable not found: {e}")
    sys.exit(1)


# --- Bot Configuration & Constants ---
WELCOME_MESSAGE = (
    "👋 Welcome! I am an AI assistant with memory. Ask me anything!\n\n"
    "Type /clear to reset my memory of our conversation.\n"
    "For more updates, join @kranthikumargoudEEE."
)
USER_DATA_FILE = "users.txt"
TELEGRAM_MAX_MESSAGE_LENGTH = 4096


# --- MarkdownV2 Escaping Function ---
def escape_markdown_v2(text: str) -> str:
    """Escapes characters for Telegram's MarkdownV2 parser."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join([f'\\{char}' if char in escape_chars else char for char in text])


# --- Helper Function: Store User Info ---
def store_user(chat_id: int, username: str, first_name: str):
    """Appends a new user's information to a text file."""
    try:
        with open(USER_DATA_FILE, "a+") as f:
            f.seek(0)
            if str(chat_id) not in f.read():
                f.write(f"{chat_id},{username},{first_name}\n")
                LOGGER.info(f"✅ New user stored: {first_name} (@{username})")
    except IOError as e:
        LOGGER.error(f"⚠️ Could not write to {USER_DATA_FILE}: {e}")


# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and clears any previous history."""
    user = update.effective_user
    if user:
        store_user(user.id, user.username or "N/A", user.first_name or "N/A")
    
    # Clear history on /start to begin a fresh conversation
    context.chat_data['history'] = []
    LOGGER.info(f"New conversation started for chat ID: {update.effective_chat.id}")
    
    await update.message.reply_text(WELCOME_MESSAGE)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clears the conversation history for the current chat."""
    context.chat_data['history'] = []
    await update.message.reply_text("✅ Memory cleared. Let's start a new conversation!")
    LOGGER.info(f"Conversation history cleared for chat ID: {update.effective_chat.id}")


# --- Message Handler: Manages AI Chat Logic ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes user messages, gets a response from OpenRouter, and replies."""
    user_input = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user
    lower_input = user_input.lower()
    
   # --- Specific Keyword Logic ---

    # Rule 1: Check for questions directed at the bot ("you" or "your")
    bot_identity_triggers = ['you', 'your']
    role_keywords = [
        "admin", "administrator", "owner", "boss", "head", "leader", "manager",
        "supervisor", "mod", "moderator", "creator", "founder", "maker",
        "builder", "developer", "contact", "support", "help", "created", "made"
    ]
    
    if any(trigger in lower_input for trigger in bot_identity_triggers) and \
       any(keyword in lower_input for keyword in role_keywords):
        await update.message.reply_text("@kranthikumargoudEEE")
        return

    # Rule 2: Check for mentions of the owner's name
    owner_names = ["kranthikumargoudEEE", "kranthikumargoud", "kranthikumar", "kranthi"]
    for name in owner_names:
        if name in lower_input:
            await update.message.reply_text(f"{name.capitalize()} is my owner and creator.")
            return

    # --- Conversation Memory Logic ---
    # Retrieve history, or create an empty list if it's the first message
    history = context.chat_data.get('history', [])
    
    # Add the new user message to the history
    history.append({"role": "user", "content": user_input})

    # Ensure user is stored
    if user:
        store_user(user.id, user.username or "N/A", user.first_name or "N/A")

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": f"{WEBHOOK_URL}",
            },
            json={
                "model": "meta-llama/llama-4-maverick",
                "messages": history,  # Send the entire conversation history
            },
            timeout=45 # Increased timeout for potentially longer context
        )
        response.raise_for_status()
        data = response.json()

        if data.get("choices") and data["choices"][0].get("message"):
            reply = data["choices"][0].get("message").get("content", "")
            # Add the AI's response to the history to be remembered
            history.append({"role": "assistant", "content": reply})
        else:
            LOGGER.error(f"API response missing 'choices' structure: {data}")
            reply = "Sorry, I received an unexpected response from the AI."

    except requests.exceptions.Timeout:
        LOGGER.warning("API request timed out.")
        reply = "Sorry, the request took too long."
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Network error during API call: {e}")
        reply = "I'm having trouble connecting to the AI service."
    except Exception as e:
        LOGGER.critical(f"An unexpected error occurred in chat handler: {e}")
        reply = "An unexpected error occurred."
        
    # Save the updated history back to the chat data for the next message
    context.chat_data['history'] = history

    # Send the reply
    safe_reply = escape_markdown_v2(reply)
    if len(safe_reply) <= TELEGRAM_MAX_MESSAGE_LENGTH:
        await update.message.reply_text(safe_reply, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        LOGGER.info("Response is too long, splitting into multiple messages.")
        for i in range(0, len(safe_reply), TELEGRAM_MAX_MESSAGE_LENGTH):
            chunk = safe_reply[i:i + TELEGRAM_MAX_MESSAGE_LENGTH]
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN_V2)


# --- Main Application Setup ---
def main() -> None:
    """Sets up and runs the Telegram bot."""
    LOGGER.info("🚀 Starting bot...")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register all command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear)) # Add the new clear command
    
    # Register the message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    port = int(os.environ.get("PORT", 10000))

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )
    LOGGER.info(f"✅ Bot is live and listening on port {port}")

if __name__ == "__main__":
    main()
