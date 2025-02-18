# api/bot.py
import telebot
from flask import Flask, request

app = Flask(__name__)

TOKEN = "7711604335:AAF-WmHthrkkIrzOyXhz07lkYFP4DqsxjuA"
bot = telebot.TeleBot(TOKEN)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

# @app.route('/')
# def index():
#     return 'Telegram Bot is running!'

if __name__ == '__main__':
    app.run(debug=True)