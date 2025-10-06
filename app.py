import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === Replace with your real tokens ===
TELEGRAM_BOT_TOKEN = "8210399902:AAFth1BQPkeaPl92UYjfCjg7YaEh9IwWtDM"
OPENROUTER_API_KEY = "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"
WEBHOOK_URL = "https://kranthikumargoudeee-ai.onrender.com"  # Your Render URL

WELCOME_MESSAGE = (
    "👋 Welcome! Join @kranthikumargoudEEE for updates.\n"
    "You may ask any questions here."
)

# --- Telegram bot app ---
bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": user_input}]},
        )
        data = response.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ API Error")
    except Exception as e:
        reply = f"❌ Something went wrong: {str(e)}"

    await update.message.reply_text(reply)

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# --- Flask server ---
flask_app = Flask(__name__)

@flask_app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    # Properly schedule update processing
    bot_app.update_queue.put_nowait(update)
    return "ok"

@flask_app.route('/')
def home():
    return "🤖 Telegram bot is live!", 200

async def set_webhook():
    await bot_app.bot.set_webhook(f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")
    print("✅ Webhook set successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())       # Set webhook once
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

