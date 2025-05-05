import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from playwright.async_api import async_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def search_vinted(item_name: str, max_price: int):
    url = f"https://www.vinted.fr/vetements?search_text={item_name}&price_to={max_price}"
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(5000)  # wait for content

        items = await page.query_selector_all("a.catalog-item")
        for item in items[:5]:
            title = await item.get_attribute("title")
            href = await item.get_attribute("href")
            price_span = await item.query_selector(".price")
            price = await price_span.inner_text() if price_span else "?"

            results.append({
                "title": title,
                "url": f"https://www.vinted.fr{href}",
                "price": price
            })

        await browser.close()

    return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue ! Envoyez-moi un message comme :\n`air force 1, 50`", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "," not in text:
        await update.message.reply_text("❌ Format invalide. Utilisez : `air force 1, 50`", parse_mode="Markdown")
        return

    item, price = text.split(",", 1)
    item = item.strip()
    try:
        max_price = int(price.strip())
    except ValueError:
        await update.message.reply_text("❌ Le prix doit être un nombre entier.", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔍 Recherche de {item} pour moins de {max_price}€...")

    try:
        results = await search_vinted(item, max_price)
        if not results:
            await update.message.reply_text("❌ Aucun article trouvé.")
            return

        for r in results:
            msg = f"👟 {r['title']}\n💶 Prix: {r['price']}\n🔗 [Voir](<{r['url']}>)"
            await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        print("Erreur:", e)
        await update.message.reply_text("❌ Une erreur s'est produite pendant la recherche.")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())