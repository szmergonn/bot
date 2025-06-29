# main.py

from openai import OpenAI
from telegram.ext import Application
import asyncio
import logging

import config
from database import db
# ПРАВИЛЬНЫЙ ОФИЦИАЛЬНЫЙ ИМПОРТ
from supabase import acreate_client, AsyncClient
from handlers import common_handlers, message_handlers, menu_handler, admin_handlers, profile_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main() -> None:
    """Основная функция, которая настраивает и запускает бота."""
    
    # Создаем асинхронный клиент Supabase ПРАВИЛЬНЫМ СПОСОБОМ
    supabase_client: AsyncClient = await acreate_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    logger.info("Подключение к Supabase (async) успешно установлено.")
    
    # Создаем клиент OpenAI
    openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Регистрируем все обработчики, передавая им нужные клиенты
    common_handlers.register_handlers(application, supabase_client)
    message_handlers.register_handlers(application, openai_client, supabase_client)
    menu_handler.register_handlers(application, supabase_client)
    admin_handlers.register_handlers(application, supabase_client)
    profile_handler.register_handlers(application, supabase_client)

    try:
        logger.info("Запуск бота...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info("Бот успешно запущен.")
        
        while True:
            await asyncio.sleep(3600)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка бота...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Бот успешно остановлен.")


if __name__ == "__main__":
    asyncio.run(main())