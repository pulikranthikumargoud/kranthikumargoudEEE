import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)

# === Replace with your real tokens ===
TELEGRAM_BOT_TOKEN = "8210399902:AAFth1BQPkeaPl92UYjfCjg7YaEh9IwWtDM"
OPENROUTER_API_KEY = "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"
WEBHOOK_URL = "https://kranthikumargoudeee-ai.onrender.com"  # Your Render URL

# Flask app for Render
flask_app = Flask(__name__)

# Telegram bot setup
application = Application.builder().token(BOT_TOKEN).build()

# === Define bot behavior ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Join @kranthikumargoudEEE for updates.\nYou may ask any questions here."
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": user_message}],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
            response_data = response.json()
            reply = response_data["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    await update.message.reply_text(reply)

# === Register handlers ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# === Webhook route ===
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok", 200

@flask_app.route("/")
def index():
    return "Bot is live! 🚀"

# === Start bot ===
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    asyncio.get_event_loop().run_until_complete(application.initialize())
    flask_app.run(host="0.0.0.0", port=PORT)

