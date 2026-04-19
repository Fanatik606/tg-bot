import asyncio
from aiogram import Bot, Dispatcher, types
from datetime import datetime

API_TOKEN = "8734151580:AAHCULS_PdWJoJlVBlZZ5E4i36nkyKbhKAQ"
ADMIN_ID = 79322727056

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message()
async def handle_message(message: types.Message):
    user = message.from_user

    username = f"@{user.username}" if user.username else "нет username"
    nickname = user.full_name
    user_id = user.id

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # текст или что-то другое
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption
    else:
        text = "не текст (фото/видео/файл)"

    msg = (
        f"📩 новое сообщение\n\n"
        f"👤 ник: {nickname}\n"
        f"🔗 юзер: {username}\n"
        f"🆔 id: {user_id}\n"
        f"🕒 время: {now}\n\n"
        f"💬 текст:\n{text}"
    )

    try:
        await bot.send_message(ADMIN_ID, msg)
    except Exception as e:
        print("ошибка отправки:", e)


async def main():
    print("бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())