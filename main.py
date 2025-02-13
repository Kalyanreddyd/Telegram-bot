import os
import time
import telebot
from flask import Flask

# Load bot token from Render environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("🚨 ERROR: BOT_TOKEN is missing! Set it in Render Environment Variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Web route (to keep Render Web Service alive)
@app.route('/')
def home():
    return "🤖 Telegram Bot is Running!"

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🤖 Hello! Your bot is running on Render Web Service!")

# Function to keep the bot running and handle crashes
def run_bot():
    while True:
        try:
            bot.polling(non_stop=True, timeout=10, long_polling_timeout=10)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
