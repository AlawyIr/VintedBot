import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from playwright.async_api import async_playwright

TOKEN = "7570253222:AAFBtrWYWrQrFHKCAP9VXvVxDwcj4P2HSOQ"

logging.basicConfig(level=logging.INFO)

# Dictionnaire pour stocker les tentatives des utilisateurs
user_attempts = {}

async def scrape_vinted(recherche: str, prix_max: float):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context()).new_page()

            url = f"https://www.vinted.fr/catalog?search_text={recherche.replace(' ', '%20')}&price_to={prix_max}"
            await page.goto(url, timeout=60000)
            await page.wait_for_selector('div.feed-grid__item', timeout=10000)

            all_articles = await page.query_selector_all('div.feed-grid__item')
            articles = all_articles[:5]
            resultats = []

            for article in articles:
                lien = await article.query_selector('a')
                titre = await article.query_selector('h3')
                prix = await article.query_selector('.feed-item__price')

                url_article = await lien.get_attribute('href') if lien else "Lien non trouvé"
                titre_txt = await titre.inner_text() if titre else "Sans titre"
                prix_txt = await prix.inner_text() if prix else "Prix inconnu"

                complet = f"{titre_txt}\n{prix_txt}\nhttps://www.vinted.fr{url_article}"
                resultats.append(complet)

            await browser.close()
            return "\n\n".join(resultats) if resultats else "Aucun article trouvé pour ta recherche."

        except Exception as e:
            return f"❌ Erreur lors du scraping : {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texte = update.message.text.strip() 

    if user_id not in user_attempts:
        user_attempts[user_id] = 2

    if user_attempts[user_id] <= 0:
        await update.message.reply_text("🚫 Tu as utilisé toutes tes tentatives. Plus aucune recherche disponible.")
        return

    if "|" not in texte:
        await update.message.reply_text(
            "❗ Utilise ce format :\n\n`nom de l'article | prix max`\n\nExemple :\n`air force 1 | 50`",
            parse_mode="Markdown"
        )
        return

    try:
        recherche, prix_max = [part.strip() for part in texte.split("|")]
        prix_max = float(prix_max)
        await update.message.reply_text("🔍 Je cherche sur Vinted...")

        resultats = await scrape_vinted(recherche, prix_max)

        # Réduction des tentatives après une recherche réussie
        user_attempts[user_id] -= 1
        await update.message.reply_text(resultats)
        await update.message.reply_text(f"📉 Il te reste {user_attempts[user_id]} tentative(s).")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Erreur : {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot lancé !")
    app.run_polling()
