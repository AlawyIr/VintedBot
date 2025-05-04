import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Make sure this is your actual Telegram bot token
TELEGRAM_TOKEN = "7630121368:AAHiVZk4ff3w2CIJRvT8jEytkeYOKLl2gCE"

# Headers with your real session cookie
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "x-csrf-token": "null",
    "x-platform": "web",
    "cookie": "_vinted_fr_session=ekRpWXpXKzhKZHZvUEwvYkVVNnZVNVpiN3RrNXpJNHIwR2tHQm1Qam9WSXNFbXVYYzJoRmxSallCRFNxcHorekRuMGVXbUVJQWdDOE0yUXJnWTdkNWxsM0g5UFZ3WWRFczJHZnY3WVVWYWpEY1krWHRCditMam1NdEtsaUhxM3JSbmpLTGkvd2pYVjhPbU12RTFEVDkrNHNzaTViMzVrNUI5dnlOV2ZYaWtlaXhCRGtIMG9lYkhGSHZRS3FhL0k3NEMxOUc2U3ZicW9vRTh1NG51b2ZDYVFhWjhqLzI1MWVXR3E2amRIbzdBTUtkY3A0MlB4MURMYWQxUTdvWTJZUjhSYUY5aTBmTU5OOVNmTXhRQlUxRWkwMHl6UWM5MlRXeEJHMlVhMWEyOHN3UUVWTTFHcnpqRlk4eDMxYzNXazFSMWQzVFl5S3ZqNkJSbmhWcTNrQW40TXBZN0szUDFPbnJTYlR5dnljRks3enZXb29Cd0RwS2FGVkFZWWJkZE1DWmJXNHhiQk90V1MvOHpIb3hvUG5lOUdZZnFhSUlCcTNQbnJjSGxMbEVqaDFDZXpKcXRMYndWZVBKRkhDcHRub1FuYzlldnJ1UisvWGxjMXZnTURoNkVRYkIrdmJFZndMS3RxUm1yYVFZb055YWM2RlJNcDV2S2o0V2pHdEt0OCtMTFJsREZrY2dDc2xjb29WNXdPTDVXNFltUmtieHB2R2UxaEpkek1zbkY0R0g2R2Uzd01ySi85NWd0aVgraEZ5WTBUVE5Bdm5Ka0F6UEI4aFhFaE1xcUlINW1ENlM2N0JQMEEwL1NkaG1JdlZFclVDYXNtdHBMV0RHWW41ek1KMC0tRzcwTWhmaHcyUGVobmVUdHFCS1RzUT09--e371f6e52ad806900ee389dc40e6feee8691e490"
}

def search_vinted(item_name: str, max_price: int):
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": item_name,
        "price_to": max_price,
        "per_page": 5
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("items", [])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Send a message like:\n`item name, max price`\nExample: `air force 1, 50`",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "," not in text:
        await update.message.reply_text("❌ Invalid format. Send like: `air force 1, 50`", parse_mode="Markdown")
        return

    item, price = text.split(",", 1)
    item = item.strip()
    try:
        max_price = int(price.strip())
    except ValueError:
        await update.message.reply_text("❌ The price must be a number.", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔍 Searching for `{item}` under {max_price}€...", parse_mode="Markdown")

    try:
        items = search_vinted(item, max_price)
        if not items:
            await update.message.reply_text("❌ No items found.")
            return

        for i in items:
            msg = f"🛍 {i['title']}\n💶 Price: {i['price']}€\n🔗 [View item](https://www.vinted.fr{i['url']})"
            await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ An error occurred while searching.")
        print("Error:", e)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
