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

    base_info = (
        f"новое сообщение\n\n"
        f"ник: {nickname}\n"
        f"юзер: {username}\n"
        f"id: {user_id}\n"
        f"время: {now}\n\n"
    )

    try:
        # если фото
        if message.photo:
            file_id = message.photo[-1].file_id

            await bot.send_photo(
                ADMIN_ID,
                photo=file_id,
                caption=base_info + f"текст:\n{text}"
            )

        # если просто текст
        else:
            await bot.send_message(
                ADMIN_ID,
                base_info + f"текст:\n{text}"
            )

    except Exception as e:
        print("ошибка отправки:", e)


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
