"""One-time script to create/authenticate the Telegram session file."""

from telegram_search.config import API_HASH, API_ID, PHONE, SESSION_PATH
from telethon.sync import TelegramClient

print("Creating session at:", SESSION_PATH)
print("Phone:", PHONE)

client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
client.start(phone=PHONE)

print("Authenticated as:", client.get_me().first_name)
print("Session file created. You can now run the server.")
client.disconnect()
