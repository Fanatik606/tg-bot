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

# антиспам
user_last_time = {}
SPAM_DELAY = 5  # секунд


def is_spam(user_id):
    now = datetime.now().timestamp()
    last = user_last_time.get(user_id, 0)

    if now - last < SPAM_DELAY:
        return True

    user_last_time[user_id] = now
    return False


def get_keyboard(text, user_info):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="анонимно в канал",
                callback_data=f"anon|{text}|{user_info}"
            )
        ],
        [
            InlineKeyboardButton(
                text="с юзером в канал",
                callback_data=f"user|{text}|{user_info}"
            )
        ]
    ])


@dp.message()
async def handle_message(message: types.Message):
    if is_spam(message.from_user.id):
        await message.answer("слишком часто, подожди немного")
        return

    user = message.from_user

    username = f"@{user.username}" if user.username else "нет username"
    nickname = user.full_name
    user_id = user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = message.text or message.caption or "нет текста"

    user_info = f"{nickname} | {username} | {user_id} | {now}"

    caption = (
        "новое сообщение\n\n"
        f"пользователь: {nickname}\n"
        f"юзер: {username}\n"
        f"id: {user_id}\n"
        f"время: {now}\n\n"
        f"текст:\n{text}"
    )

    try:
        if message.photo:
            file_id = message.photo[-1].file_id

            await bot.send_photo(
                ADMIN_ID,
                photo=file_id,
                caption=caption,
                reply_markup=get_keyboard(text, user_info)
            )
        else:
            await bot.send_message(
                ADMIN_ID,
                caption,
                reply_markup=get_keyboard(text, user_info)
            )

    except Exception as e:
        print("ошибка:", e)


@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data
    action, text, user_info = data.split("|", 2)

    if action == "anon":
        post = f"💬 анонимный пост\n\n{text}"

    else:
        post = f"💬 пост\n\n{text}\n\n👤 {user_info}"

    await bot.send_message(CHANNEL_ID, post)
    await callback.answer("опубликовано в канал")


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
