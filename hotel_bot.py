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
if __name__ == "__main__":
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

    import os

    print("Starting Telegram bot...")
    bot_token = os.environ["BOT_TOKEN"]
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running and ready.")

    app.run_polling()