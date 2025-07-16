import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Example /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Welcome to Budget Hotel Finder Bot!\n\n"
        "📍 Send your location to find nearby budget hotels.\n"
        "💡 Use /help for assistance."
    )

# Example /help handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send your live location to get nearby budget hotels.\n"
        "If you face issues, please try again or contact support."
    )

def main():
    # Pull the bot token from environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set in Railway environment.")
        return

    # Build application
    app = ApplicationBuilder().token(bot_token).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("✅ Bot is running and ready.")
    app.run_polling()

if __name__ == '__main__':
    main()