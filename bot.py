import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

CHANNEL_ID = "@overheard_pvl"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_last_time = {}
SPAM_DELAY = 3


def is_spam(user_id):
    now = datetime.now().timestamp()
    last = user_last_time.get(user_id, 0)

    if now - last < SPAM_DELAY:
        return True

    user_last_time[user_id] = now
    return False


def keyboard(message_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="анонимно", callback_data=f"anon:{message_id}"),
            InlineKeyboardButton(text="с юзером", callback_data=f"user:{message_id}")
        ]
    ])


messages_cache = {}


@dp.message()
async def handle_message(message: types.Message):
    if is_spam(message.from_user.id):
        return

    user = message.from_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = message.text or message.caption or "нет текста"

    msg_id = str(message.message_id)

    messages_cache[msg_id] = {
        "user": user,
        "text": text,
        "time": now
    }

    caption = f"новое сообщение\n\n{user.full_name}\n{text}"

    try:
        if message.photo:
            await bot.send_photo(
                ADMIN_ID,
                message.photo[-1].file_id,
                caption=caption,
                reply_markup=keyboard(msg_id)
            )
        else:
            await bot.send_message(
                ADMIN_ID,
                caption,
                reply_markup=keyboard(msg_id)
            )
    except Exception as e:
        print("error:", e)


@dp.callback_query()
async def callback_handler(call: types.CallbackQuery):
    data = call.data
    action, msg_id = data.split(":")

    msg = messages_cache.get(msg_id)
    if not msg:
        await call.answer("сообщение не найдено")
        return

    user = msg["user"]
    text = msg["text"]

    if action == "anon":
        post = f"💬 анонимный пост\n\n{text}"
    else:
        post = f"💬 пост\n\n{text}\n\n👤 @{user.username if user.username else 'нет username'}"

    await bot.send_message(CHANNEL_ID, post)
    await call.answer("опубликовано")


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
