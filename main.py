import random
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# 🔐 Telegram Bot Token
BOT_TOKEN = "7713211393:AAEUh5lug3dizn85fhjLGV9b3a4UVr8exi8"
API_ID = 23200475
API_HASH = "644e1d9e8028a5295d6979bb3a36b23b"

# 🔄 User cooldowns (store last time they used the command)
user_cooldowns = {}

# 🧠 List of available accounts (replace with your actual accounts)
accounts = [
    "Email: user1@example.com | Pass: pass123",
    "Email: user2@example.com | Pass: qwerty!",
    "Email: user3@example.com | Pass: hello123",
    "Email: user4@example.com | Pass: test@123",
    "Email: user5@example.com | Pass: mypass456",
    "Email: user6@example.com | Pass: rockyou",
    "Email: user7@example.com | Pass: newlogin2024",
    "Email: user8@example.com | Pass: pass@789",
]

# 🕒 Cooldown time in seconds (24 hours)
COOLDOWN_SECONDS = 24 * 60 * 60

# ⚙️ Start the bot
app = Client("random_account_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply("👋 Hello! Use /get to receive 2 random accounts (every 24 hours only).")

@app.on_message(filters.command("get"))
async def send_accounts(client, message: Message):
    user_id = message.from_user.id
    now = time.time()

    # Check cooldown
    if user_id in user_cooldowns and now - user_cooldowns[user_id] < COOLDOWN_SECONDS:
        remaining = int((COOLDOWN_SECONDS - (now - user_cooldowns[user_id])) / 3600)
        await message.reply(f"⏳ Please wait {remaining} more hour(s) before using this command again.")
        return

    # Update cooldown
    user_cooldowns[user_id] = now

    # Send two unique random accounts
    selected = random.sample(accounts, 2)
    msg = f"🎁 Here are your random accounts:\n\n1. {selected[0]}\n2. {selected[1]}"
    await message.reply(msg)

app.run()
