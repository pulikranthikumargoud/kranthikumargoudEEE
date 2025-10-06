import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- YOUR TOKENS ---
TELEGRAM_BOT_TOKEN = "8210399902:AAFth1BQPkeaPl92UYjfCjg7YaEh9IwWtDM"
OPENROUTER_API_KEY = "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"

# --- START MESSAGE ---
WELCOME_MESSAGE = (
    "👋 Welcome! Join @kranthikumargoudEEE for other updates.\n"
    "You may ask any questions here."
)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

# --- Message Handler ---
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
            error_message = data.get("error", {}).get("message", "Unknown error from API.")
            reply = f"⚠️ API Error: {error_message}"

    except Exception as e:
        reply = f"❌ Something went wrong: {str(e)}"

    await update.message.reply_text(reply)


# --- Run Bot ---
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
from flask import Flask
import threading

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running fine! 🚀"

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_flask).start()

