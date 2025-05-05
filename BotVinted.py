import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from playwright.async_api import async_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def search_vinted(item_name, max_price):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = f"https://www.vinted.fr/catalog?search_text={item_name}&price_to={max_price}"
        await page.goto(url)
        await page.wait_for_timeout(3000)

        items = await page.locator('[data-testid="item-box"]').all()
        results = []

        for item in items[:5]:
            title = await item.locator("h3").inner_text()
            price = await item.locator('[data-testid="item-price"]').inner_text()
            href = await item.locator("a").get_attribute("href")
            results.append({
                "title": title,
                "price": price,
                "url": href,
            })

        await browser.close()
        return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue ! Envoyez-moi un message comme ceci :\n`nom de l'article, prix max`\nEx: `air force 1, 50`",
        parse_mode="Markdown",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "," not in text:
        await update.message.reply_text(
            "❌ Format invalide. Envoyez comme ceci : `air force 1, 50`",
            parse_mode="Markdown",
        )
        return

    item, price = text.split(",", 1)
    item = item.strip()
    try:
        max_price = int(price.strip())
    except ValueError:
        await update.message.reply_text(
            "❌ Le prix doit être un nombre entier.", parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"🔍 Recherche de `{item}` pour moins de {max_price}€...", parse_mode="Markdown"
    )

    try:
        items = await search_vinted(item, max_price)
        if not items:
            await update.message.reply_text("❌ Aucun article trouvé.")
            return

        for i in items:
            msg = f"👟 {i['title']}\n💶 Prix: {i['price']}\n🔗 [Voir l'article](https://www.vinted.fr{i['url']})"
            await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ Une erreur s'est produite.")
        print("Erreur:", e)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
