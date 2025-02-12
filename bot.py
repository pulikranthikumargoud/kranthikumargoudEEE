from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "7770532717:AAG3WxD-8PtSbAg190idxLFE-JDA2w94CWI"

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your @kranthikumargoudEEE. Send me your doubt!")

# Function to handle normal text messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()

    if user_message in ["hi", "hello"]:
        await update.message.reply_text("Hello! How can I help you?")
    elif "doubt" in user_message:
        await update.message.reply_text("Please describe your doubt, I will try to assist!")
    else:
        await update.message.reply_text("I didn't understand. Please rephrase your question.")

# Main function to run the bot
def main():
    app = Application.builder().token(TOKEN).build()

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
