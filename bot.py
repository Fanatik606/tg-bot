import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = "@overheard_pvl"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

storage = {}


def keyboard(msg_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="анонимно", callback_data=f"anon:{msg_id}"),
            InlineKeyboardButton(text="с юзером", callback_data=f"user:{msg_id}")
        ]
    ])


# /start
@dp.message(lambda m: m.text == "/start")
async def start_cmd(message: types.Message):
    user = message.from_user

    await message.answer(
        "привет 👋\n"
        "просто отправь сообщение или фото, и оно попадёт в систему"
    )

    # уведомление тебе
    try:
        await bot.send_message(
            ADMIN_ID,
            f"👤 новый пользователь нажал /start\n"
            f"{user.full_name} | @{user.username if user.username else 'нет username'} | {user.id}"
        )
    except:
        pass


# обычные сообщения
@dp.message()
async def handler(message: types.Message):
    user = message.from_user

    text = message.text or message.caption or "нет текста"

    # ❌ игнорируем /start полностью дальше
    if text == "/start":
        return

    username = f"@{user.username}" if user.username else "нет username"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    photo = message.photo[-1].file_id if message.photo else None
    msg_id = str(message.message_id)

    storage[msg_id] = {
        "text": text,
        "photo": photo,
        "user": user,
        "username": username,
        "time": now
    }

    admin_msg = (
        "📩 новое сообщение\n\n"
        f"👤 {user.full_name}\n"
        f"🔗 {username}\n"
        f"🆔 {user.id}\n"
        f"⏰ {now}\n\n"
        f"💬 {text}"
    )

    # уведомление тебе (дублируем факт отправки)
    try:
        if photo:
            await bot.send_photo(ADMIN_ID, photo, caption=admin_msg, reply_markup=keyboard(msg_id))
        else:
            await bot.send_message(ADMIN_ID, admin_msg, reply_markup=keyboard(msg_id))
    except:
        pass


@dp.callback_query()
async def callback(call: types.CallbackQuery):
    action, msg_id = call.data.split(":")

    data = storage.get(msg_id)
    if not data:
        await call.answer("нет данных")
        return

    text = data["text"]
    photo = data["photo"]

    if action == "anon":
        caption = f"💬 анонимный пост\n\n{text}"
    else:
        u = data["user"]
        caption = (
            f"💬 пост\n\n{text}\n\n"
            f"👤 @{u.username if u.username else 'нет username'}"
        )

    try:
        if photo:
            await bot.send_photo(CHANNEL_ID, photo, caption=caption)
        else:
            await bot.send_message(CHANNEL_ID, caption)

        await call.answer("опубликовано")

    except Exception as e:
        print("channel error:", e)
        await call.answer("ошибка")


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
