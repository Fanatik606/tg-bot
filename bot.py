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

user_last_time = {}
SPAM_DELAY = 5


RULES_TEXT = """
📌 правила подслушано павлодара

здесь публикуются сообщения о людях, ситуациях и всем, что происходит вокруг

важно:
допускаются личные мнения и резкие высказывания
но ответственность за достоверность остаётся на авторе

если информация оказалась недостоверной:
отправь пост в бот повторно
он будет проверен и удалён при подтверждении

запрещено:
- заведомо ложная информация с целью навредить
- личные данные (адреса, телефоны и тд)
- угрозы и призывы к насилию
- спам

администрация может удалять материалы без объяснений
"""


def is_spam(user_id):
    now = datetime.now().timestamp()
    last = user_last_time.get(user_id, 0)

    if now - last < SPAM_DELAY:
        return True

    user_last_time[user_id] = now
    return False


def keyboard(msg_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔒 анонимно", callback_data=f"anon:{msg_id}"),
            InlineKeyboardButton(text="👤 с юзером", callback_data=f"user:{msg_id}")
        ],
        [
            InlineKeyboardButton(text="❌ отклонить", callback_data=f"reject:{msg_id}")
        ]
    ])


# /start
@dp.message(lambda m: m.text == "/start")
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 правила", callback_data="rules")]
    ])

    await message.answer(
        "привет 👋\nотправь сообщение или фото",
        reply_markup=kb
    )


# правила
@dp.callback_query(lambda c: c.data == "rules")
async def rules(call: types.CallbackQuery):
    await call.message.answer(RULES_TEXT)
    await call.answer()


# сообщения
@dp.message()
async def handler(message: types.Message):

    if is_spam(message.from_user.id):
        await message.answer("слишком часто, подожди немного")
        return

    user = message.from_user
    text = message.text or message.caption or ""

    if text == "/start":
        return

    now = datetime.now(ZoneInfo("Asia/Almaty")).strftime("%Y-%m-%d %H:%M:%S")

    username = f"@{user.username}" if user.username else "нет username"
    full_name = user.full_name or "без имени"

    photo = message.photo[-1].file_id if message.photo else None
    msg_id = str(message.message_id)

    storage[msg_id] = {
        "text": text,
        "photo": photo,
        "user_id": user.id,
        "username": username,
        "full_name": full_name,
        "chat_id": message.chat.id
    }

    admin_text = (
        "📩 новое сообщение\n\n"
        f"👤 имя: {full_name}\n"
        f"🔗 юзер: {username}\n"
        f"🆔 id: {user.id}\n"
        f"⏰ {now}\n\n"
        f"💬 {text}"
    )

    try:
        if photo:
            await bot.send_photo(
                ADMIN_ID,
                photo,
                caption=admin_text,
                reply_markup=keyboard(msg_id)
            )
        else:
            await bot.send_message(
                ADMIN_ID,
                admin_text,
                reply_markup=keyboard(msg_id)
            )

        await message.answer("сообщение отправлено ✔")

    except Exception as e:
        print("error:", e)
        await message.answer("ошибка отправки")


# модерация
@dp.callback_query()
async def callback(call: types.CallbackQuery):

    if call.data == "rules":
        return

    action, msg_id = call.data.split(":")

    data = storage.get(msg_id)
    if not data:
        await call.answer("нет данных")
        return

    text = data["text"]
    photo = data["photo"]
    chat_id = data["chat_id"]
    username = data["username"]
    full_name = data["full_name"]

    # ❌ отклонение
    if action == "reject":
        try:
            await bot.send_message(
                chat_id,
                "❌ твой пост был отклонён модерацией"
            )

            await call.message.delete()

        except Exception as e:
            print("reject error:", e)

        await call.answer("отклонено")
        return

    # 💬 аноним
    if action == "anon":
        caption = f"💬 анонимный пост\n\n{text}"

    # 👤 с юзером
    elif action == "user":
        caption = (
            f"💬 пост\n\n{text}\n\n"
            f"👤 {full_name}\n"
            f"🔗 {username}"
        )
    else:
        return

    try:
        if photo:
            await bot.send_photo(CHANNEL_ID, photo, caption=caption)
        else:
            await bot.send_message(CHANNEL_ID, caption)

        await call.message.edit_text("✅ опубликовано")
        await call.answer("готово")

    except Exception as e:
        print("channel error:", e)
        await call.answer("ошибка")


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
