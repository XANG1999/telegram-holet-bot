import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from utils import fetch_hotels_from_api, log_user_interaction

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_interaction(user, "start")
    button = KeyboardButton("📍 Share Current Location", request_location=True)
    markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Welcome! Share your location to find budget-friendly hotels nearby.", reply_markup=markup)

# Handle location
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    loc = update.message.location
    lat, lon = loc.latitude, loc.longitude
    log_user_interaction(user, "location", f"{lat},{lon}")
    await update.message.reply_text("Fetching budget-friendly hotels near you...")

    hotels = fetch_hotels_from_api(lat, lon, radius_km=10, max_results=5)

    if not hotels:
        await update.message.reply_text("No hotels found nearby.")
        return

    for hotel in hotels:
        text = (
            f"🏨 *{hotel['name']}*\n"
            f"💰 Price: ₹{hotel['price']}\n"
            f"📍 Location: {hotel['location']}\n"
            f"📏 Distance: {hotel['distance']} km"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Book Now", url=hotel['link'])]])
        await update.message.reply_markdown(text, reply_markup=keyboard)

# /help command
import asyncio

async def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    # add other handlers

    print("Bot is running and ready.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()
    await app.stop()
    await app.shutdown()

if __name__ == '__main__':
    asyncio.run(main())