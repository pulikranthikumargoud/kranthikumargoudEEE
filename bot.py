import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace this with your OpenRouter API Key
API_KEY = "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"

# Replace this with your Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7770532717:AAG3WxD-8PtSbAg190idxLFE-JDA2w94CWI"

# OpenRouter API function
def query_openrouter(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-r1:free",  # You can use "gpt-3.5-turbo", "gpt-4", etc.
        "messages": [{"role": "user", "content": user_message}]
    }

    response = requests.post(url, json=data, headers=headers)

    # Debugging: Print API response for errors
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    try:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    except requests.exceptions.JSONDecodeError:
        return "Error: Unable to decode AI response."

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your @kranthikumargoudEEE Send me a your doubt.")

# AI chat function
async def chat(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    ai_response = query_openrouter(user_message)
    await update.message.reply_text(ai_response)

# Main function
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
