import asyncio
import os
from aiogram import Bot, Dispatcher, types
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    user = message.from_user

    username = f"@{user.username}" if user.username else "нет username"
    nickname = user.full_name
    user_id = user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = message.text or message.caption or "нет текста"

    caption = (
        "📩 новое сообщение\n\n"
        f"👤 пользователь: {nickname}\n"
        f"🔗 юзер: {username}\n"
        f"🆔 id: {user_id}\n"
        f"⏰ время: {now}\n\n"
        f"💬 сообщение:\n{text}"
    )

    try:
        # если есть фото
        if message.photo:
            file_id = message.photo[-1].file_id

            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=file_id,
                caption=caption
            )

        # если текста нет фото
        else:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=caption
            )

    except Exception as e:
        print("ошибка:", e)


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
