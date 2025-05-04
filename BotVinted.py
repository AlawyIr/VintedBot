import requests
import time
import os
from playwright.sync_api import sync_playwright
import telegram

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def search_vinted(item, max_price):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        url = f"https://www.vinted.fr/vetements?search_text={item}&price_to={max_price}"
        page.goto(url)
        page.wait_for_timeout(5000)  # wait for JS to load

        content = page.content()
        hrefs = page.eval_on_selector_all("a[href^='/items/']", "elements => elements.map(e => e.href)")
        browser.close()

        unique_links = list(set(hrefs))[:5]
        return unique_links

def handle_message(text):
    try:
        item, price = text.split(",", 1)
        item = item.strip()
        price = int(price.strip())
        results = search_vinted(item, price)

        if results:
            for link in results:
                bot.send_message(chat_id=CHAT_ID, text=link)
        else:
            bot.send_message(chat_id=CHAT_ID, text="No items found.")
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text="❌ Invalid format. Send like: `air force 1, 50`")

def main():
    last_update = 0
    while True:
        updates = bot.get_updates()
        if updates:
            latest = updates[-1]
            if latest.update_id > last_update:
                last_update = latest.update_id
                msg = latest.message.text
                handle_message(msg)
        time.sleep(5)

if __name__ == "__main__":
    main()
