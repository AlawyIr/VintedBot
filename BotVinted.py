import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TELEGRAM_TOKEN = "7630121368:AAHiVZk4ff3w2CIJRvT8jEytkeYOKLl2gCE"
CHAT_ID = "5596101074"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "x-csrf-token": "null",
    "x-platform": "web",
    "cookie": "eHhwZDAvTjU0Vm5mT0R2anQySzVhUnBKUEJPZkFWQ3FYRm5jNFNEMTVuM1Jyb3pEYkRDNkJyZUVQUzUyMittbjR3NTJscTRvbUtSR2xEajQ2NDdNblUybmE3akdOaHJUM2VHYm5DS0ZrVUtaWmZReGh4UzZVRXpkaHkvcVlvOGtkTlF5Y3lVTnJhS1gzeXEzNnF6eThqcGwyWVpiT3c2bkhIei8rdkhzdVI4SWpRU0Q2c0RzdGpKYks3VU9Tc2MvSFFFRUNKdWFiN3NZQm0ySzJXbkp4QWFlWW9ZeFl6ZTdYb2I4TTJZWUVwRGZZblRkM294ck9ZODZXMFpnNkw1dEJWb3hTclZ5eGlVclhibnZDM3dyWXkzUjRCMGZqSkNIT3J1KzBiaGxPME1seHBybzI4ZHdRYkZJdGNJYWNnRWNsK002VngzNWFHSm9RMW5YNGdlbWRVTVduZkhsRFExSHY5UHMrQXdPcml0YlBoZFZvNTIyS2NJcXVOS21XMFlkOXhzLzdsVEs4WEJGdlFpZ1lNOEduVUY1ZVRwL1NONUtHMnQyTmlJcEVGeXV6d21QNHBUT1BJdW9CNU03OU4xcGtXWkYraFFIdjhyeEp2dkg1dkl2SktjcUo2bk4rTHY0TDZYd0cyS3RmaEQ2NlpwcXFYdXlNcTdlNVpqTWJzb0greERxZWlYejB3VEJTeTVlcXkvZFZzY0FhT2VvVis3amdWY3U2Vm8zZTNXTnZYSkJJNXV6ZDFxTkIzZm1FMVNCODhmUXFvUDRaTmdHdU4reTZFdmNHOXl2aGRsOGpHdElJdkVmZldJMHRyWkpCZUJPZDNUakVJZlBwSG4vWE9UWC0tU09mU3ZwMzV4UUJCby9QdkhuakROQT09--c514e85fa80cff344dab15d1789d71a3d0ea5111"
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
        "👋 Bienvenue ! Envoyez-moi un message sous la forme :\n"
        "`nom de l'article, prix max`\nExemple : `air force 1, 50`",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "," not in text:
        await update.message.reply_text("❌ Format invalide. Envoyez comme ceci : `air force 1, 50`", parse_mode="Markdown")
        return

    item, price = text.split(",", 1)
    item = item.strip()
    try:
        max_price = int(price.strip())
    except ValueError:
        await update.message.reply_text("❌ Le prix doit être un nombre entier. Réessayez.", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔍 Recherche de `{item}` pour moins de {max_price}€...", parse_mode="Markdown")

    try:
        items = search_vinted(item, max_price)
        if not items:
            await update.message.reply_text("❌ Aucun article trouvé.")
            return

        for i in items:
            title = i.get("title", "Titre inconnu")
            price = i.get("price", {}).get("amount", "?")
            currency = i.get("price", {}).get("currency", "€")
            url = "https://www.vinted.fr" + i.get("url", "")
            msg = f"👟 {title}\n💶 Prix: {price} {currency}\n🔗 [Voir l'article]({url})"
            await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ Une erreur s'est produite pendant la recherche.")
        print("Erreur:", e)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
