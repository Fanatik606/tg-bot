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

# хранение сообщений
storage = {}

# антиспам
user_last_time = {}
SPAM_DELAY = 5


RULES_TEXT = """
📌 правила подслушано павлодара

здесь публикуются сообщения о людях, ситуациях и всем, что происходит вокруг

важно:
допускаются резкие высказывания и личные мнения
но ответственность за достоверность информации остаётся на авторе

если опубликованная информация о человеке оказалась недостоверной:
отправь этот пост обратно в бот
он будет проверен
при подтверждении недостоверности пост будет удалён

запрещено:
публикация заведомо ложной информации с целью навредить человеку
распространение личных данных (доксинг, адреса, номера телефонов)
угрозы и призывы к насилию
спам

администрация оставляет за собой право удалять любые материалы без объяснений
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
            InlineKeyboardButton(text="опубликовать", callback_data=f"post:{msg_id}"),
            InlineKeyboardButton(text="отклонить", callback_data=f"reject:{msg_id}")
        ]
    ])


# /start
@dp.message(lambda m: m.text == "/start")
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 правила", callback_data="rules")]
    ])

    await message.answer(
        "привет 👋\n"
        "отправь сообщение или фото",
        reply_markup=kb
    )


# правила кнопка
@dp.callback_query(lambda c: c.data == "rules")
async def rules(call: types.CallbackQuery):
    await call.message.answer(RULES_TEXT)
    await call.answer()


# обработка сообщений
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

    photo = message.photo[-1].file_id if message.photo else None
    msg_id = str(message.message_id)

    storage[msg_id] = {
        "text": text,
        "photo": photo,
        "user": user,
        "time": now
    }

    admin_text = (
        "📩 новое сообщение\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 {user.id}\n"
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

    if call.data.startswith("rules"):
        return

    action, msg_id = call.data.split(":")

    data = storage.get(msg_id)
    if not data:
        await call.answer("нет данных")
        return

    text = data["text"]
    photo = data["photo"]

    # отклонение
    if action == "reject":
        await call.message.edit_text("❌ пост отклонён")
        await call.answer("отклонено")
        return

    # публикация
    if action == "post":

        caption = f"💬 пост\n\n{text}"

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
