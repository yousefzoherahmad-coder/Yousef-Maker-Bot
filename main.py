import os, asyncio, aiohttp, aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# --- الإعدادات ---
BOT_TOKEN = "8335720065:AAHxhaElFfMAyClCebzKhGtjDtkb0flGUQI"
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_states = {}

# --- سيرفر Flask وهمي لإرضاء Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot Factory is Running!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# --- وظائف الذكاء الاصطناعي ---
async def ask_gpt(prompt):
    if not OPENAI_KEY: return "⚠️ عذراً، خدمة الذكاء الاصطناعي غير مفعّلة في الإعدادات."
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            if resp.status == 200:
                res = await resp.json()
                return res['choices'][0]['message']['content']
            return "❌ حدث خطأ في الاتصال بالذكاء الاصطناعي."

# --- الأزرار ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 إنشاء بوت جديد", callback_data="create")],
        [InlineKeyboardButton(text="🧠 اسأل الذكاء الاصطناعي", callback_data="ai_ask")],
        [InlineKeyboardButton(text="👨‍💻 المطور", url="https://t.me/fi1_o")]
    ])

# --- المعالجات ---
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🔥 مرحباً بك في بوت الخدمات المتكاملة!\nاختر ما تريد القيام به:", reply_markup=main_menu())

@dp.callback_query(F.data == "ai_ask")
async def ai_mode(call: types.CallbackQuery):
    user_states[call.from_user.id] = "chatting"
    await call.message.answer("🆗 أنا أسمعك.. أرسل سؤالك الآن وسأجيبك فوراً:")

@dp.callback_query(F.data == "create")
async def create_mode(call: types.CallbackQuery):
    user_states[call.from_user.id] = "creating"
    await call.message.answer("📥 أرسل توكن البوت الخاص بك من @BotFather:")

@dp.message()
async def handle_text(msg: types.Message):
    state = user_states.get(msg.from_user.id)
    
    if state == "chatting":
        await msg.answer("⏳ أفكر...")
        response = await ask_gpt(msg.text)
        await msg.answer(response)
    
    elif state == "creating" and ":" in msg.text:
        await msg.answer(f"✅ تم استلام التوكن وجاري ربطه بالصناعة..")
        # هنا يمكنك إضافة كود حفظ التوكن في الداتا بيز
    
    else:
        await msg.answer("استخدم الأزرار بالأعلى للتحكم بالبوت ☝️")

# --- التشغيل ---
async def main():
    Thread(target=run_flask).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
            
