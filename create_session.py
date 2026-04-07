"""One-time script to create/authenticate the Telegram session file."""
import os

from telethon.sync import TelegramClient

API_ID = int(os.environ.get("TELEGRAM_API_ID", "13500944"))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "03ef9adf59670f3ae824c0ad1bec5a48")
PHONE = os.environ.get("TELEGRAM_PHONE", "+79119125372")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(PROJECT_DIR, "telegram_session")

print("Creating session at:", SESSION_PATH)
print("Phone:", PHONE)

client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
client.start(phone=PHONE)

print("Authenticated as:", client.get_me().first_name)
print("Session file created. You can now run server.py.")
client.disconnect()
