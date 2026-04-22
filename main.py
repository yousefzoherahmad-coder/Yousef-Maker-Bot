import telebot
from telebot import types
import os
from flask import Flask
import threading

# --- نظام إيهام Render (Keep Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    # Render يطلب تشغيل السيرفر على هذا المنفذ تحديداً
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

# تشغيل السيرفر الوهمي في الخلفية
keep_alive()

# --- كود البوت الخاص بك ---
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

# تشغيل عملية الاستقبال
print("LEX-Ω System: Bot is starting...")
bot.infinity_polling()
    
