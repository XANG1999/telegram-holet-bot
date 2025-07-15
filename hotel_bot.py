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

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🚀 Google Sheets setup
def get_sheet():
    creds_json = json.loads(os.environ["GSHEET_CREDS"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Hotel Listings").sheet1
    return sheet

# 🚀 Fetch matching listings from the sheet
def search_listings(query):
    sheet = get_sheet()
    records = sheet.get_all_records()
    query_lower = query.lower()

    results = []
    for record in records:
        tags = record["Tags"].lower()
        type_ = record["Type"].lower()
        location = record["Location"].lower()
        if any(word in tags or word in location or word in type_ for word in query_lower.split()):
            results.append(record)
    return results

# 🚀 /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send me what you're looking for (e.g., 'cheap homestay in Goa').")

# 🚀 Message handler for user queries
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    listings = search_listings(query)

    if listings:
        for listing in listings[:3]:  # Limit to top 3 matches
            msg = (
                f"🏡 *{listing['Name']}*\n"
                f"📍 {listing['Location']}\n"
                f"💰 {listing['Price']} per night\n"
                f"🔗 [Book Now]({listing['Link']})"
            )
            await update.message.reply_markdown(msg)
    else:
        await update.message.reply_text("❌ No matching listings found. Please try different keywords.")

# 🚀 Main bot setup
async def main():
    print("Starting Telegram bot...")
    bot_token = os.environ["BOT_TOKEN"]
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running and ready.")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
