import os
import json
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Global variables
COUNTRIES = {
    "germany": "Germany", "ukraine": "Ukraine", "kazakhstan": "Kazakhstan",
    "russia": "Russia", "belarus": "Belarus", "china": "China",
    "hongkong": "Hong Kong", "poland": "Poland", "england": "England",
    "romania": "Romania", "czech": "Czech", "sweden": "Sweden"
}

# Load used numbers from file
try:
    with open("used_numbers.json", "r") as f:
        used_numbers = json.load(f)
except FileNotFoundError:
    used_numbers = {}

# Save used numbers to file
def save_used_numbers():
    with open("used_numbers.json", "w") as f:
        json.dump(used_numbers, f)

# Get available numbers from OnlineSim
def get_numbers():
    try:
        response = requests.get("https://onlinesim.io/api/getFreePhoneList")
        return response.json().get("numbers", [])
    except:
        return []

# Get random unused number for user
def get_random_number(user_id):
    user_id = str(user_id)
    numbers = get_numbers()
    
    if not numbers:
        return None, None
    
    # Get user's used numbers or initialize
    user_used = used_numbers.get(user_id, [])
    
    # Filter new numbers
    available = [
        num for num in numbers 
        if num["free"] and num["online"] and num["number"] not in user_used
    ]
    
    if not available:
        return None, None
    
    # Choose random new number
    chosen = random.choice(available)
    number = chosen["number"]
    country = chosen["country"]
    
    # Update used numbers
    user_used.append(number)
    used_numbers[user_id] = user_used
    save_used_numbers()
    
    return number, country

# Get messages for number
def get_messages(number):
    try:
        response = requests.get(f"https://onlinesim.io/api/getFreePhoneMessageList?phone={number}")
        return response.json().get("messages", [])[:5]  # Last 5 messages
    except:
        return []

# Start command handler
def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🌟 Welcome to Temp Number Bot!\n"
        "Use /number to get a new virtual number\n"
        "Each number will be unique and never repeated!"
    )

# Number command handler
def number_command(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    number, country = get_random_number(user_id)
    
    if not number:
        update.message.reply_text("⚠️ No new numbers available! Try again later")
        return
    
    # Create buttons
    keyboard = [
        [InlineKeyboardButton("🔄 Renew Number", callback_data=f"renew_{number}")],
        [InlineKeyboardButton("📬 Check Inbox", callback_data=f"inbox_{number}")],
        [InlineKeyboardButton("ℹ️ Number Info", callback_data=f"info_{number}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send response
    update.message.reply_text(
        f"✅ New Number Generated!\n\n"
        f"📱 Number: `{number}`\n"
        f"🌎 Country: {country}\n\n"
        "Choose an option:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Button click handler
def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    # Renew number request
    if data.startswith("renew_"):
        query.answer()
        number, country = get_random_number(user_id)
        
        if not number:
            query.edit_message_text("⚠️ No new numbers available! Try again later")
            return
        
        # Update buttons
        keyboard = [
            [InlineKeyboardButton("🔄 Renew Number", callback_data=f"renew_{number}")],
            [InlineKeyboardButton("📬 Check Inbox", callback_data=f"inbox_{number}")],
            [InlineKeyboardButton("ℹ️ Number Info", callback_data=f"info_{number}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update message
        query.edit_message_text(
            f"🔄 Number Renewed!\n\n"
            f"📱 New Number: `{number}`\n"
            f"🌎 Country: {country}\n\n"
            "Choose an option:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    # Inbox request
    elif data.startswith("inbox_"):
        number = data.split("_")[1]
        messages = get_messages(number)
        
        if not messages:
            query.answer("📭 Inbox is empty! No messages found", show_alert=True)
            return
        
        # Format messages
        msg_text = f"📬 Last 5 Messages for `{number}`:\n\n"
        for msg in messages:
            msg_text += f"⏰ {msg['created_at']}\n✉️ {msg['text']}\n\n"
        
        query.answer()
        query.edit_message_text(
            msg_text,
            parse_mode="Markdown"
        )
    
    # Number info request
    elif data.startswith("info_"):
        number = data.split("_")[1]
        query.answer()
        query.edit_message_text(
            f"ℹ️ Number Information\n\n"
            f"📱 Number: `{number}`\n"
            f"🔒 This number is 100% new and unique\n"
            f"✅ Never used before in this bot\n"
            f"💡 Tip: Use for OTP verification immediately",
            parse_mode="Markdown"
        )

# Main function
def main():
    # Get token from environment variable or file
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        try:
            with open("src/token.txt", "r") as f:
                TOKEN = f.read().strip()
        except FileNotFoundError:
            print("Error: Bot token not found!")
            return
    
    # Create updater
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("number", number_command))
    dispatcher.add_handler(CommandHandler("help", start_command))
    dispatcher.add_handler(CallbackQueryHandler(button_click))
    
    # Start bot
    print("Bot started! Press Ctrl+C to stop")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
