import asyncio
from telegram import Bot

async def send_test_message():
    bot = Bot(token="7905737995:AAE2ByX1Lg4OyMk5tkBvkKpFJNDmUxLKfP8")
    chat_id = "5596101074"
    await bot.send_message(chat_id=chat_id, text="Test: Vinted bot is working!")

# Run the async function
asyncio.run(send_test_message())