# api/bot.py
import telebot
import os
import json
from flask import Flask, request

TOKEN = "7711604335:AAF-WmHthrkkIrzOyXhz07lkYFP4DqsxjuA"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return 'Telegram Bot is running!'

if __name__ == '__main__':
    app.run(debug=True)