# main.py

from openai import OpenAI
from telegram.ext import Application
from telegram import BotCommandScopeAllPrivateChats
import asyncio
import logging

import config
from database import db
# ПРАВИЛЬНЫЙ ОФИЦИАЛЬНЫЙ ИМПОРТ
from supabase import acreate_client, AsyncClient
from handlers import common_handlers, message_handlers, menu_handler, admin_handlers, profile_handler, voice_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def setup_bot_commands(application):
    """Настраивает меню команд бота для разных языков."""
    
    # Команды для русских пользователей
    russian_commands = [
        ("start", "🚀 Начать работу с ботом"),
        ("menu", "📱 Открыть главное меню"),  
        ("balance", "💰 Проверить баланс кредитов"),
        ("profile", "👤 Личный кабинет")
    ]
    
    # Команды для английских пользователей  
    english_commands = [
        ("start", "🚀 Start using the bot"),
        ("menu", "📱 Open main menu"),
        ("balance", "💰 Check credit balance"), 
        ("profile", "👤 User profile")
    ]
    
    # Команды для польских пользователей
    polish_commands = [
        ("start", "🚀 Rozpocznij korzystanie z bota"),
        ("menu", "📱 Otwórz menu główne"),
        ("balance", "💰 Sprawdź saldo kredytów"),
        ("profile", "👤 Profil użytkownika")
    ]
    
    try:
        # Устанавливаем команды для всех пользователей (русский по умолчанию)
        await application.bot.set_my_commands(russian_commands)
        logger.info("✅ Установлены команды по умолчанию (русский)")
        
        # Устанавливаем команды для конкретных языков
        
        # Для русскоязычных пользователей
        await application.bot.set_my_commands(
            commands=russian_commands,
            scope=BotCommandScopeAllPrivateChats(),
            language_code="ru"
        )
        logger.info("✅ Установлены команды для русского языка")
        
        # Для англоязычных пользователей  
        await application.bot.set_my_commands(
            commands=english_commands,
            scope=BotCommandScopeAllPrivateChats(),
            language_code="en"
        )
        logger.info("✅ Установлены команды для английского языка")
        
        # Для польскоязычных пользователей
        await application.bot.set_my_commands(
            commands=polish_commands,
            scope=BotCommandScopeAllPrivateChats(),
            language_code="pl"
        )
        logger.info("✅ Установлены команды для польского языка")
        
        logger.info("🎉 Меню команд настроено для всех языков!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при настройке команд: {e}")

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
    voice_handler.register_handlers(application, openai_client, supabase_client)

    try:
        logger.info("Запуск бота...")
        await application.initialize()
        
        # НОВОЕ: Настраиваем многоязычное меню команд
        await setup_bot_commands(application)
        
        await application.start()
        await application.updater.start_polling()
        logger.info("🚀 Бот успешно запущен с многоязычным меню!")
        
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