import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables (Set your API keys here)
TELEGRAM_BOT_TOKEN = "7770532717:AAG3WxD-8PtSbAg190idxLFE-JDA2w94CWI"
OPENROUTER_API_KEY = "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"

app = Flask(__name__)

# Function to send requests to OpenRouter API
def query_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    data = {"model": "deepseek/deepseek-r1:free", "prompt": prompt, "max_tokens": 300}
    
    response = requests.post("https://openrouter.ai/api/chat", json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
    return "Error in OpenRouter API request."

# Telegram Bot Handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! i am your @kranthikumargoudEEE . ask your doubt! .")

async def chat(update: Update, context: CallbackContext):
    user_message = update.message.text
    ai_response = query_openrouter(user_message)
    await update.message.reply_text(ai_response)

# Initialize Telegram bot
def main():
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("Bot is running...")
    bot.run_polling()

if __name__ == "__main__":
    main()
