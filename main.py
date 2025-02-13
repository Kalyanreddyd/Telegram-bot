import os
import telebot
from flask import Flask

# Load bot token from Render environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("🚨 ERROR: BOT_TOKEN is missing! Set it in Render Environment Variables.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Create a Flask app to prevent "No open ports detected" error
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot is Running!"

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🤖 Hello! Your bot is running on Render Web Service!")

# Function to run Telegram bot
def run_bot():
    bot.polling()

if __name__ == "__main__":
    from threading import Thread
    
    # Start Telegram bot in a separate thread
    Thread(target=run_bot).start()
    
    # Start Flask web server (Render requires an open port)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
