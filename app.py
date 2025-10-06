import os
import requests
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === Replace with your real tokens ===
TELEGRAM_BOT_TOKEN = "8210399902:AAFth1BQPkeaPl92UYjfCjg7YaEh9IwWtDM"
OPENROUTER_API_KEY = "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"
WEBHOOK_URL = "https://kranthikumargoudeee-ai.onrender.com"  # Your Render URL

# --- Start message ---
WELCOME_MESSAGE = (
    "👋 Welcome! Join @kranthikumargoudEEE for other updates.\n"
    "You may ask any questions here."
)

# --- Helper: Store user info ---
def store_user(chat_id, username, first_name):
    with open("users.txt", "a") as f:
        f.write(f"{chat_id},{username},{first_name}\n")
    print(f"✅ Stored user: {first_name} (@{username}), chat_id={chat_id}")

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    username = update.message.from_user.username or "N/A"
    first_name = update.message.from_user.first_name or "N/A"

    # Log and store user
    print(f"User started the bot: {first_name} (@{username}), chat_id={chat_id}")
    store_user(chat_id, username, first_name)

    # Reply to user
    await update.message.reply_text(WELCOME_MESSAGE)
    await update.message.reply_text(f"Your chat ID is: {chat_id}")

# --- Message Handler ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_id = update.message.chat_id

    # Store user if not already stored
    username = update.message.from_user.username or "N/A"
    first_name = update.message.from_user.first_name or "N/A"
    store_user(chat_id, username, first_name)

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://render.com",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": user_input}],
            },
        )
        data = response.json()

        if "choices" in data:
            reply = data["choices"][0]["message"]["content"]
        else:
            reply = f"⚠️ API Error: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        reply = f"❌ Something went wrong: {str(e)}"

    await update.message.reply_text(reply)

# --- Proactive messaging function ---
def send_proactive_message(text):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    if not os.path.exists("users.txt"):
        print("No users found to send messages.")
        return

    with open("users.txt", "r") as f:
        users = f.readlines()

    for line in users:
        chat_id, username, first_name = line.strip().split(",", 2)
        try:
            bot.send_message(chat_id=int(chat_id), text=text)
            print(f"✅ Message sent to {first_name} (@{username}), chat_id={chat_id}")
        except Exception as e:
            print(f"❌ Failed to send message to {chat_id}: {e}")

# --- Main ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Run webhook
    PORT = int(os.environ.get("PORT", 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )

    print(f"✅ Bot is live at {WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")
    print("📌 Users will be stored automatically for proactive messaging.")
