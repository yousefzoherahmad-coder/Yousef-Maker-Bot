import os
import asyncio
import aiohttp
import aiosqlite
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update, BufferedInputFile

# ================= الإعدادات (Config) =================
BOT_TOKEN = "8335720065:AAHxhaElFfMAyClCebzKhGtjDtkb0flGUQI"
DEVELOPER_ID = 123456789  # ضع الآيدي الخاص بك هنا
BASE_URL = "https://yousef-maker-bot.onrender.com"
FORCE_CHANNEL = "@yousef_zoher"

# مفاتيح الخدمات (سيتم جلبها من إعدادات ريندر)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_KEY = os.getenv("DEEPL_API_KEY")
REMOVE_BG_KEY = os.getenv("REMOVE_BG_KEY")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY")

# ================= الخدمات (Services) =================
async def ai_chat(prompt):
    if not OPENAI_KEY: return "⚠️ مفتاح AI غير متوفر"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    json = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json=json) as r:
            data = await r.json()
            return data["choices"][0]["message"]["content"]

async def translate_text(text):
    if not DEEPL_KEY: return "⚠️ مفتاح الترجمة غير متوفر"
    url = "https://api-free.deepl.com/v2/translate"
    data = {"auth_key": DEEPL_KEY, "text": text, "target_lang": "EN"}
    async with aiohttp.ClientSession() as s:
        async with s.post(url, data=data) as r:
            res = await r.json()
            return res["translations"][0]["text"]

# ================= المحرك الأساسي (Core) =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)
active_bots = {}
user_states = {}

async def init_db():
    async with aiosqlite.connect("data.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS bots (id INTEGER PRIMARY KEY, owner_id INTEGER, token TEXT, username TEXT)")
        await db.commit()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 إنشاء بوت", callback_data="create")],
        [InlineKeyboardButton(text="📂 بوتاتي", callback_data="my_bots")],
        [InlineKeyboardButton(text="👨‍💻 المطور", url="https://t.me/fi1_o")]
    ])

def bot_services_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 ذكاء اصطناعي", callback_data="ai"), InlineKeyboardButton(text="🌐 ترجمة", callback_data="trans")],
        [InlineKeyboardButton(text="🎙️ تحويل صوت", callback_data="tts"), InlineKeyboardButton(text="🖼️ حذف خلفية", callback_data="bg")],
        [InlineKeyboardButton(text="🎨 كلمات لصور", callback_data="t2i")]
    ])

# ================= التعامل مع الرسائل (Handlers) =================
@dp.message(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer(f"🏭 أهلاً بك في مصنع البوتات الاحترافي!", reply_markup=main_menu())

@dp.callback_query()
async def handle_callbacks(call: types.CallbackQuery):
    if call.data == "create":
        await call.message.answer("📥 أرسل توكن البوت الجديد الآن:")
    elif call.data in ["ai", "trans", "tts", "bg", "t2i"]:
        user_states[call.from_user.id] = call.data
        await call.message.answer("🆗 أرسل طلبك الآن (نص أو صورة حسب الخدمة):")

@dp.message()
async def handle_all_messages(msg: types.Message):
    state = user_states.get(msg.from_user.id)
    
    # إذا كان يرسل توكن لإنشاء بوت
    if ":" in msg.text and len(msg.text) > 20:
        try:
            temp_bot = Bot(token=msg.text)
            me = await temp_bot.get_me()
            async with aiosqlite.connect("data.db") as db:
                await db.execute("INSERT INTO bots(owner_id, token, username) VALUES(?,?,?)", (msg.from_user.id, msg.text, me.username))
                await db.commit()
            await msg.answer(f"✅ تم تشغيل بوتك بنجاح: @{me.username}")
        except:
            await msg.answer("❌ التوكن غير صحيح!")
    
    # التعامل مع الخدمات المدمجة
    elif state == "ai":
        res = await ai_chat(msg.text)
        await msg.answer(res)
    elif state == "trans":
        res = await translate_text(msg.text)
        await msg.answer(res)
    else:
        await msg.answer("الرجاء اختيار خدمة من القائمة أو إرسال توكن.")

# ================= الويب هوك (Webhooks) =================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook_main():
    update = Update(**request.json)
    await dp.feed_update(bot, update)
    return "OK"

@app.route("/")
def home(): return "Bot Factory is Running!"

# ================= التشغيل (Execution) =================
async def on_startup():
    await init_db()
    await bot.set_webhook(f"{BASE_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=10000)
            
