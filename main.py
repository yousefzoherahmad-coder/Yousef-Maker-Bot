import os
import asyncio
import aiohttp
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ================= الإعدادات =================
BOT_TOKEN = "8335720065:AAHxhaElFfMAyClCebzKhGtjDtkb0flGUQI"

# مفاتيح الخدمات (يجب إضافتها في Environment Variables بموقع Render لتفعيلها)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_KEY = os.getenv("DEEPL_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_states = {}

async def init_db():
    async with aiosqlite.connect("data.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS bots (id INTEGER PRIMARY KEY, owner_id INTEGER, token TEXT, username TEXT)")
        await db.commit()

# ================= أزرار التحكم القوية =================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 إنشاء بوت جديد", callback_data="create")],
        [InlineKeyboardButton(text="🧠 ذكاء اصطناعي (GPT)", callback_data="ai"), InlineKeyboardButton(text="🌐 ترجمة (DeepL)", callback_data="trans")],
        [InlineKeyboardButton(text="👨‍💻 المطور", url="https://t.me/fi1_o")]
    ])

# ================= الخدمات (Services) =================
async def ai_chat(prompt):
    if not OPENAI_KEY: return "⚠️ خدمة الذكاء الاصطناعي غير مفعلة حالياً."
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json=payload) as r:
            data = await r.json()
            return data["choices"][0]["message"]["content"]

# ================= المعالجات (Handlers) =================
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(f"🚀 أهلاً بك في البوت الخارق!\n\nاختر الخدمة التي تريدها من الأسفل:", reply_markup=main_menu())

@dp.callback_query()
async def handle_callbacks(call: types.CallbackQuery):
    if call.data == "create":
        await call.message.answer("📥 أرسل توكن البوت (من @BotFather) لإنشائه فوراً:")
    elif call.data == "ai":
        user_states[call.from_user.id] = "ai"
        await call.message.answer("🆗 أنا جاهز.. أرسل سؤالك للذكاء الاصطناعي:")
    elif call.data == "trans":
        user_states[call.from_user.id] = "trans"
        await call.message.answer("🌐 أرسل النص الذي تريد ترجمته للإنجليزية:")

@dp.message()
async def handle_all_messages(msg: types.Message):
    state = user_states.get(msg.from_user.id)
    
    # إذا كان يرسل توكن (إنشاء بوت)
    if msg.text and ":" in msg.text and len(msg.text) > 20:
        await msg.answer("⏳ جاري فحص التوكن وتشغيل البوت الجديد...")
        try:
            temp_bot = Bot(token=msg.text)
            me = await temp_bot.get_me()
            async with aiosqlite.connect("data.db") as db:
                await db.execute("INSERT INTO bots(owner_id, token, username) VALUES(?,?,?)", (msg.from_user.id, msg.text, me.username))
                await db.commit()
            await msg.answer(f"✅ تم بنجاح!\nبوتك الجديد أصبح متاحاً هنا: @{me.username}")
        except:
            await msg.answer("❌ التوكن الذي أرسلته غير صالح.")
    
    # تنفيذ خدمات الذكاء الاصطناعي
    elif state == "ai":
        res = await ai_chat(msg.text)
        await msg.answer(res)
    else:
        await msg.answer("الرجاء اختيار خدمة من القائمة بالأعلى ☝️")

# ================= التشغيل =================
async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
            
