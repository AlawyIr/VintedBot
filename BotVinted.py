import asyncio
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

logging.basicConfig(level=logging.INFO)

async def search_vinted(item_name, max_price):
    url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={item_name}&price_to={max_price}&per_page=5"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            await browser.close()

        data = json.loads(content)
        items = data.get("items", [])
        if not items:
            return "❌ Aucun article trouvé."

        results = "\n\n".join(
            f"👟 {item['title']}\n💶 {item['price']}€\n🔗 https://www.vinted.fr{item['url']}"
            for item in items
        )
        return results

    except Exception as e:
        logging.error(f"Erreur de recherche : {e}")
        return "❌ Une erreur s'est produite."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Recherche de air force 1 pour moins de 50€...")
    result = await search_vinted("air force 1", 50)
    await update.message.reply_text(result)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

import nest_asyncio
nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

