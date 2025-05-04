import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Set your Telegram bot token here
BOT_TOKEN = "7630121368:AAHiVZk4ff3w2CIJRvT8jEytkeYOKLl2gCE"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Search function for Vinted items
def search_vinted(query: str, max_price: int, limit: int = 5):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = f"https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": query,
        "price_to": max_price,
        "per_page": limit
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me your search like this:\n\n`air force 1, 50`",
        parse_mode="Markdown"
    )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if ',' in text:
        try:
            item, price = map(str.strip, text.split(',', 1))
            price = int(price)
            await update.message.reply_text(f"🔍 Searching for '{item}' under €{price}...")

            items = search_vinted(item, price)

            if not items:
                await update.message.reply_text("❌ No items found.")
                return

            for item in items:
                title = item.get("title")
                price = item.get("price", {}).get("amount")
                currency = item.get("price", {}).get("currency")
                url = f"https://www.vinted.fr{item.get('url')}"
                photo = item.get("photo", {}).get("url")

                text = f"🛍️ *{title}*\n💸 {price} {currency}\n🔗 [View Listing]({url})"
                await update.message.reply_photo(photo=photo, caption=text, parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Couldn't read the price. Please send like: `air force 1, 50`")
    else:
        await update.message.reply_text("❌ Invalid format. Please send like: `air force 1, 50`")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
