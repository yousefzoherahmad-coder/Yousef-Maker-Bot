import telebot
from telebot import types

# التوكن الخاص بك
API_TOKEN = '8335720065:AAHxhaElFfMAyClCebzKhGtjDtkb0flGUQI'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 صنع بوت جديد"), types.KeyboardButton("📊 إحصائيات"))
    bot.send_message(message.chat.id, f"أهلاً بك {message.from_user.first_name} في مصنعك! 🏭", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🚀 صنع بوت جديد")
def ask_token(message):
    bot.send_message(message.chat.id, "ارسل توكن البوت الجديد من @BotFather:")

bot.polling(none_stop=True)
  
