import telebot
import schedule
import time
import threading
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram bot token (Use Railway environment variable)
BOT_TOKEN = os.getenv("BOT_TOKEN")  
CHANNELS_FILE = "channels.json"  # Stores user-entered channels
SCHEDULE_FILE = "schedule.json"  # Stores scheduled messages
FORWARD_GROUP_ID = -1001234567890  # Replace with your group ID to auto-forward messages

bot = telebot.TeleBot(BOT_TOKEN)

# Load saved channels
def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    return []

# Save channels
def save_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

# Load scheduled messages
def load_scheduled_messages():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    return []

# Save scheduled messages
def save_scheduled_messages(messages):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(messages, f)

# Inline button creator
def create_inline_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Visit Website", url="https://example.com"))
    markup.add(InlineKeyboardButton("📢 Join Our Channel", url="https://t.me/example_channel"))
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🤖 Welcome! Use /setchannels to add/update your channel list.\nUse /schedule to schedule messages.")

@bot.message_handler(commands=["setchannels"])
def set_channels(message):
    bot.reply_to(message, "📢 Send me a list of Telegram channel usernames (comma-separated):")

@bot.message_handler(func=lambda message: message.text and message.text.startswith("@"))
def save_user_channels(message):
    channels = [ch.strip() for ch in message.text.split(",")]
    save_channels(channels)
    bot.reply_to(message, "✅ Channels saved! Send a message or media, and I'll forward it.")

@bot.message_handler(commands=["schedule"])
def schedule_message(message):
    bot.reply_to(message, "📅 Send your message in this format:\n`Message | YYYY-MM-DD HH:MM`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: "|" in message.text and len(message.text.split("|")) == 2)
def save_schedule(message):
    text, datetime_str = message.text.split("|")
    scheduled_messages = load_scheduled_messages()
    scheduled_messages.append({"text": text.strip(), "time": datetime_str.strip()})
    save_scheduled_messages(scheduled_messages)
    bot.reply_to(message, "✅ Message scheduled!")

def check_scheduled_messages():
    while True:
        scheduled_messages = load_scheduled_messages()
        for msg in scheduled_messages:
            text = msg["text"]
            time_str = msg["time"]

            if time.strftime("%Y-%m-%d %H:%M") == time_str:
                channels = load_channels()
                for channel in channels:
                    bot.send_message(channel, text)
                scheduled_messages.remove(msg)
                save_scheduled_messages(scheduled_messages)
        time.sleep(60)

@bot.message_handler(content_types=["text", "photo", "video", "document"])
def forward_content(message):
    channels = load_channels()
    
    for channel in channels:
        try:
            if message.text:
                bot.send_message(channel, message.text, reply_markup=create_inline_buttons())
            elif message.photo:
                bot.send_photo(channel, message.photo[-1].file_id, caption=message.caption or "", reply_markup=create_inline_buttons())
            elif message.video:
                bot.send_video(channel, message.video.file_id, caption=message.caption or "", reply_markup=create_inline_buttons())
            elif message.document:
                bot.send_document(channel, message.document.file_id, caption=message.caption or "", reply_markup=create_inline_buttons())
            
            bot.reply_to(message, f"✅ Sent to {channel}")
        except Exception as e:
            bot.reply_to(message, f"❌ Error sending to {channel}: {e}")

@bot.message_handler(func=lambda message: message.chat.id == FORWARD_GROUP_ID)
def auto_forward(message):
    channels = load_channels()
    for channel in channels:
        bot.copy_message(chat_id=channel, from_chat_id=message.chat.id, message_id=message.message_id)

# Start the scheduled message checker in a separate thread
threading.Thread(target=check_scheduled_messages, daemon=True).start()

print("Bot is running...")
bot.polling()
