import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("7630121368:AAHiVZk4ff3w2CIJRvT8jEytkeYOKLl2gCE")
CHAT_ID = os.getenv("5596101074")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def search_vinted(item_name: str, max_price: int):
    url = f"https://www.vinted.fr/api/v2/catalog/items"
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
    await update.message.reply_text("👋 Bienvenue ! Envoyez-moi un message sous la forme :\n`nom de l'article, prix max`\nExemple : `air force 1, 50`", parse_mode="Markdown")

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
            msg = f"👟 {i['title']}\n💶 Prix: {i['price']}€\n🔗 [Voir l'article](https://www.vinted.fr{ i['url'] })"
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
