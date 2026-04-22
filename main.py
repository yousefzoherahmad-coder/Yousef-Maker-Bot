import os
import asyncio
import aiohttp
import aiosqlite
from flask import Flask, request
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update
from aiogram.filters import Command

# ================= الإعدادات (Config) =================
BOT_TOKEN = "8335720065:AAHxhaElFfMAyClCebzKhGtjDtkb0flGUQI"
BASE_URL = "https://yousef-maker-bot.onrender.com"

# مفاتيح الخدمات (تأكد من إضافتها في Environment Variables بموقع Render)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_KEY = os.getenv("DEEPL_API_KEY")

# ================= المحرك الأساسي (Core) =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)
user_states = {}

async def init_db():
    async with aiosqlite.connect("data.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS bots (id INTEGER PRIMARY KEY, owner_id INTEGER, token TEXT, username TEXT)")
        await db.commit()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 إنشاء بوت", callback_data="create")],
        [InlineKeyboardButton(text="👨‍💻 المطور", url="https://t.me/fi1_o")]
    ])

# ================= التعامل مع الرسائل (Handlers) =================
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(f"🏭 أهلاً بك في مصنع البوتات!", reply_markup=main_menu())

@dp.callback_query(F.data == "create")
async def handle_create(call: types.CallbackQuery):
    await call.message.answer("📥 أرسل توكن البوت الجديد الآن:")

@dp.message()
async def handle_all_messages(msg: types.Message):
    if msg.text and ":" in msg.text and len(msg.text) > 20:
        try:
            temp_bot = Bot(token=msg.text)
            me = await temp_bot.get_me()
            async with aiosqlite.connect("data.db") as db:
                await db.execute("INSERT INTO bots(owner_id, token, username) VALUES(?,?,?)", (msg.from_user.id, msg.text, me.username))
                await db.commit()
            await msg.answer(f"✅ تم تشغيل بوتك بنجاح: @{me.username}")
            await temp_bot.session.close()
        except:
            await msg.answer("❌ التوكن غير صحيح أو البوت معطل!")
    else:
        await msg.answer("الرجاء إرسال توكن صحيح.")

# ================= الويب هوك (Webhooks) =================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook_main():
    if request.headers.get("content-type") == "application/json":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        update = Update.model_validate(request.json, context={"bot": bot})
        loop.run_until_complete(dp.feed_update(bot, update))
        return "OK", 200
    return "Forbidden", 403

@app.route("/")
def home(): return "Bot Factory is Running!"

# ================= التشغيل (Execution) =================
async def on_startup():
    await init_db()
    await bot.set_webhook(f"{BASE_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=10000)
        
