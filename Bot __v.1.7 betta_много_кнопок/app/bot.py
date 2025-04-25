# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.config import TOKEN


async def main():
    # Инициализация бота с токеном из конфигурации
    bot = Bot(token=TOKEN)

    # Инициализация диспетчера для обработки сообщений
    dp = Dispatcher()

    # Подключение роутера с обработчиками сообщений
    dp.include_router(router)

    # Запуск бота в режиме polling (постоянное ожидание новых сообщений)
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Настройка логирования для вывода информации в консоль
    logging.basicConfig(level=logging.INFO)

    try:
        # Запуск асинхронной функции main
        asyncio.run(main())
    except KeyboardInterrupt:
        # Обработка прерывания работы бота (например, Ctrl+C)
        print('Бот выключен')
    except Exception as e:
        # Логирование ошибок, если они возникнут
        logging.error(f"Произошла ошибка: {e}")