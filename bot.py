import asyncio
import os
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not API_TOKEN:
    raise ValueError("нет api_token")

if not ADMIN_ID:
    raise ValueError("нет admin_id")

ADMIN_ID = int(ADMIN_ID)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()


@router.message()
async def handler(message: types.Message):
    try:
        user = message.from_user

        username = f"@{user.username}" if user.username else "нет username"
        name = user.full_name or "без имени"
        text = message.text or message.caption or "медиа без текста"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info = (
            f"новое сообщение\n"
            f"время: {now}\n"
            f"ник: {name}\n"
            f"юзер: {username}\n"
            f"id: {user.id}\n"
            f"текст: {text}"
        )

        await bot.send_message(ADMIN_ID, info)

        if message.content_type != "text":
            await bot.copy_message(
                chat_id=ADMIN_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )

    except TelegramBadRequest as e:
        logging.error(f"telegram ошибка: {e}")
    except Exception as e:
        logging.error(f"ошибка: {e}")


@router.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("бот работает")


async def main():
    dp.include_router(router)
    logging.info("бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())import asyncio
import os
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not API_TOKEN:
    raise ValueError("нет api_token")

if not ADMIN_ID:
    raise ValueError("нет admin_id")

ADMIN_ID = int(ADMIN_ID)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()


def build_info(message: types.Message) -> str:
    user = message.from_user

    username = f"@{user.username}" if user.username else "нет username"
    nickname = user.full_name or "без имени"
    user_id = user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = message.text or message.caption or "не текст (медиа или файл)"

    return (
        f"<b>новое сообщение</b>\n\n"
        f"<b>ник:</b> {nickname}\n"
        f"<b>юзер:</b> {username}\n"
        f"<b>id:</b> {user_id}\n"
        f"<b>время:</b> {now}\n\n"
        f"<b>текст:</b>\n{text}"
    )


@router.message()
async def handle_message(message: types.Message):
    try:
        info = build_info(message)

        await bot.send_message(ADMIN_ID, info)

        if message.content_type != "text":
            await bot.copy_message(
                chat_id=ADMIN_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )

    except TelegramBadRequest as e:
        logging.error(f"telegram ошибка: {e}")
    except Exception as e:
        logging.error(f"ошибка: {e}")


@router.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("бот работает")


async def main():
    dp.include_router(router)
    logging.info("бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())import asyncio
import os
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not API_TOKEN:
    raise ValueError("нет api_token в переменных окружения")

if not ADMIN_ID:
    raise ValueError("нет admin_id в переменных окружения")

ADMIN_ID = int(ADMIN_ID)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()


@router.message(F.from_user)
async def handle_message(message: types.Message):
    user = message.from_user

    username = f"@{user.username}" if user.username else "нет username"
    nickname = user.full_name or "без имени"
    user_id = user.id

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = message.text or message.caption or "не текст (медиа/файл/стикер)"

    msg = (
        f"новое сообщение\n\n"
        f"ник: {nickname}\n"
        f"юзер: {username}\n"
        f"id: {user_id}\n"
        f"время: {now}\n\n"
        f"текст:\n{text}"
    )

    try:
        await bot.send_message(ADMIN_ID, msg)
    except TelegramBadRequest as e:
        logging.error(f"ошибка telegram: {e}")
    except Exception as e:
        logging.error(f"неизвестная ошибка: {e}")


@router.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("бот работает")


async def main():
    dp.include_router(router)
    logging.info("бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
