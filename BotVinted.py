import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from playwright.async_api import async_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Put your bot token in Railway's environment variables

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

async def search_vinted(item_name: str, max_price: int):
    results = []
    url = f"https://www.vinted.fr/vetements?search_text={item_name.replace(' ', '+')}&price_to={max_price}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector('[data-testid="item-box"]', timeout=10000)
        items = await page.query_selector_all('[data-testid="item-box"]')

        for item in items[:5]:  # Limit to 5 items
            title = await item.query_selector_eval('a[data-testid="item-title"]', 'el => el.textContent')
            price = await item.query_selector_eval('div[data-testid="item-box-price"]', 'el => el.textContent')
            link = await item.query_selector_eval('a[data-testid="item-title"]', 'el => el.href')
            results.append((title.strip(), price.strip(), link.strip()))

        await browser.close()
    return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue sur le bot Vinted !\n\nEnvoyez un message comme :\n`air force 1, 50`\n(prix en euros)",
        parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "," not in text:
        await update.message.reply_text("❌ Format invalide. Envoyez comme : `air force 1, 50`", parse_mode="Markdown")
        return

    item, price = text.split(",", 1)
    item = item.strip()
    try:
        max_price = int(price.strip())
    except ValueError:
        await update.message.reply_text("❌ Le prix doit être un nombre entier.", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔍 Recherche de `{item}` pour moins de {max_price}€...", parse_mode="Markdown")
    try:
        listings = await search_vinted(item, max_price)
        if not listings:
            await update.message.reply_text("❌ Aucun article trouvé.")
            return

        for title, price, link in listings:
            await update.message.reply_text(f"👟 {title}\n💶 {price}\n🔗 {link}")
    except Exception as e:
        print("Erreur:", e)
        await update.message.reply_text("❌ Une erreur est survenue pendant la recherche.")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
