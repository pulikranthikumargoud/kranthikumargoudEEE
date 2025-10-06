import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === Replace with your real tokens ===
TELEGRAM_BOT_TOKEN = "8210399902:AAFth1BQPkeaPl92UYjfCjg7YaEh9IwWtDM"
OPENROUTER_API_KEY = "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"
WEBHOOK_URL = "https://kranthikumargoudeee-ai.onrender.com"  # Your Render URL

# --- Start message ---
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
            reply = f"⚠️ API Error: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        reply = f"❌ Something went wrong: {str(e)}"

    await update.message.reply_text(reply)


if __name__ == "__main__":
    # --- Build bot application ---
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # --- Add handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # --- Run webhook ---
    PORT = int(os.environ.get("PORT", 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )

    print(f"✅ Bot is live at {WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")
