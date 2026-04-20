import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from zoneinfo import ZoneInfo

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = "@overheard_pvl"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

storage = {}
accepted_users = set()
user_last_time = {}

SPAM_DELAY = 5


def keyboard(msg_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="анонимно", callback_data=f"anon:{msg_id}"),
            InlineKeyboardButton(text="с юзером", callback_data=f"user:{msg_id}")
        ],
        [
            InlineKeyboardButton(text="❌ отклонить", callback_data=f"del:{msg_id}")
        ]
    ])


def rules_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="принять правила", callback_data="accept_rules")]
    ])


def is_spam(user_id):
    now = datetime.now().timestamp()
    last = user_last_time.get(user_id, 0)

    if now - last < SPAM_DELAY:
        return True

    user_last_time[user_id] = now
    return False


# /start
@dp.message(lambda m: m.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "привет, перед началом необходимо ознакомиться с правилами подслушки\n\n"
        "важно:\n"
        "> допускаются резкие высказывания и личные мнения\n"
        "> но ответственность за достоверность информации остаётся на авторе\n\n"
        "если информация о человеке оказалась недостоверной:\n"
        "> отправь пост обратно в бот\n"
        "> он будет проверен и удалён при необходимости\n\n"
        "запрещено:\n"
        "> публикация заведомо ложной информации с целью навредить человеку\n"
        "> распространение личных данных (адреса, телефоны)\n"
        "> угрозы и призывы к насилию\n"
        "> спам\n\n"
        "администрация может удалять материалы без объяснений",
        reply_markup=rules_keyboard()
    )


# сообщения
@dp.message()
async def handler(message: types.Message):
    user = message.from_user

    if user.id not in accepted_users:
        await message.answer("сначала прими правила")
        return

    if is_spam(user.id):
        await message.answer("не спамь")
        return

    text = message.text or message.caption or ""

    if text == "/start":
        return

    now = datetime.now(ZoneInfo("Asia/Almaty")).strftime("%Y-%m-%d %H:%M:%S")
    username = f"@{user.username}" if user.username else "нет username"

    photo = message.photo[-1].file_id if message.photo else None
    msg_id = str(message.message_id)

    storage[msg_id] = {
        "text": text,
        "photo": photo,
        "user": user,
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

    try:
        if photo:
            await bot.send_photo(ADMIN_ID, photo, caption=admin_msg, reply_markup=keyboard(msg_id))
        else:
            await bot.send_message(ADMIN_ID, admin_msg, reply_markup=keyboard(msg_id))

        await message.answer("сообщение отправлено ✔")

    except Exception as e:
        print(e)


# callback
@dp.callback_query()
async def callback(call: types.CallbackQuery):
    data = call.data

    if data == "accept_rules":
        accepted_users.add(call.from_user.id)
        await call.message.edit_text("правила приняты ✔")
        return

    action, msg_id = data.split(":")
    data_msg = storage.get(msg_id)

    if not data_msg:
        await call.answer("нет данных")
        return

    user = data_msg["user"]
    text = data_msg["text"]
    photo = data_msg["photo"]

    if action == "anon":
        caption = f"💬 анонимный пост\n\n{text}"

        if photo:
            await bot.send_photo(CHANNEL_ID, photo, caption=caption)
        else:
            await bot.send_message(CHANNEL_ID, caption)

    elif action == "user":
        caption = (
            f"💬 пост\n\n{text}\n\n"
            f"👤 @{user.username if user.username else 'нет username'}"
        )

        if photo:
            await bot.send_photo(CHANNEL_ID, photo, caption=caption)
        else:
            await bot.send_message(CHANNEL_ID, caption)

    elif action == "del":
        await call.message.delete()
        await call.answer("удалено")
        return

    await call.answer("готово")


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
