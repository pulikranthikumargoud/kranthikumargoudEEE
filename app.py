import os
import requests
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === Replace with your real tokens ===
TELEGRAM_BOT_TOKEN = "8210399902:AAFth1BQPkeaPl92UYjfCjg7YaEh9IwWtDM"
OPENROUTER_API_KEY = "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"
WEBHOOK_URL = "https://kranthikumargoudeee-ai.onrender.com"  # Your Render URL

# --- Initialize Flask app ---
flask_app = Flask(__name__)

# --- Telegram setup ---
bot = Bot(token=TELEGRAM_BOT_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# --- Start command ---
WELCOME_MESSAGE = (
    "👋 Welcome! Join @kranthikumargoudEEE for other updates.\n"
    "You may ask any questions here."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

# --- Chat handler ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
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

# --- Add handlers ---
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# --- Webhook route ---
@flask_app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await app.initialize()   # ✅ This line fixes your error
    await app.process_update(update)
    return "ok", 200

# --- Home route ---
@flask_app.route("/")
def home():
    return "🤖 Telegram bot is live on Render!", 200

# --- Set webhook automatically ---
async def set_webhook():
    await bot.set_webhook(f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")
    print("✅ Webhook set successfully!")

if __name__ == "__main__":
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
