import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from handlers import common_handlers, create_and_edit_handlers, run_handlers
from config import token

# from aiogram.fsm.storage.redis import RedisStorage, Redis

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    # Инициализируем бот и диспетчер
    bot = Bot(token=token,
              parse_mode='HTML')
    # redis = Redis(host='localhost')
    # storage = RedisStorage(redis=redis)
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(common_handlers.router)
    dp.include_router(create_and_edit_handlers.router)
    dp.include_router(run_handlers.router)

    bot_commands = [
        BotCommand(command="/start", description="Главное меню")
    ]
    await bot.set_my_commands(bot_commands)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
