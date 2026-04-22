import os
import asyncio
import aiohttp
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ================= الإعدادات =================
BOT_TOKEN = "8335720065:AAHxhaElFfMAyClCebzKhGtjDtkb0flGUQI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def init_db():
    async with aiosqlite.connect("data.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS bots (id INTEGER PRIMARY KEY, owner_id INTEGER, token TEXT, username TEXT)")
        await db.commit()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 إنشاء بوت", callback_data="create")],
        [InlineKeyboardButton(text="👨‍💻 المطور", url="https://t.me/fi1_o")]
    ])

# ================= المعالجات =================
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(f"🏭 أهلاً بك في مصنع البوتات الخاص بك!", reply_markup=main_menu())

@dp.callback_query(F.data == "create")
async def handle_create(call: types.CallbackQuery):
    await call.message.answer("📥 أرسل توكن البوت الجديد الآن:")

@dp.message()
async def handle_messages(msg: types.Message):
    if msg.text and ":" in msg.text:
        await msg.answer("⏳ جاري التحقق من التوكن...")
    else:
        await msg.answer("الرجاء اختيار خدمة من القائمة.")

# ================= التشغيل =================
async def main():
    await init_db()
    print("Bot is starting...")
    # حذف الويب هوك القديم ليعمل نظام Polling بدون تعارض
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
