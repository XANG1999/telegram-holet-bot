from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

TYPE, BUDGET, LOCATION = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! What are you looking for?",
        reply_markup=ReplyKeyboardMarkup([
            ["Hotel", "Homestay", "Restaurant"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return TYPE

async def type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['type'] = update.message.text
    await update.message.reply_text(
        "Choose your budget:",
        reply_markup=ReplyKeyboardMarkup([
            ["Low", "Medium", "High"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return BUDGET

async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['budget'] = update.message.text
    await update.message.reply_text(
        "Please share your location:",
        reply_markup=ReplyKeyboardMarkup([
            [KeyboardButton("Share Location", request_location=True)]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return LOCATION

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_location = update.message.location
    context.user_data['location'] = user_location

    response = (
        f"Here are some {context.user_data['type']} options within your {context.user_data['budget']} budget:\n"
        f"1️⃣ Blue Sky Hotel - $30/night\n"
        f"2️⃣ Cozy Homestay - $15/night\n"
        f"3️⃣ Foodie's Hub Restaurant - $5 avg/meal\n"
        "Reply with the number to get booking details."
    )

    await update.message.reply_text(response)
    return ConversationHandler.END

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, type_handler)],
        BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget_handler)],
        LOCATION: [MessageHandler(filters.LOCATION, location_handler)],
    },
    fallbacks=[CommandHandler('start', start)]
)

app.add_handler(conv_handler)
app.run_polling()
