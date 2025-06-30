# config.py

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# --- Основные токены и ключи ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Ключи для Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Настройки бота ---
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Список ID администраторов бота (может быть несколько через запятую)
ADMIN_USER_IDS_STR = os.getenv("ADMIN_USER_IDS", "")
ADMIN_USER_IDS = [int(id.strip()) for id in ADMIN_USER_IDS_STR.split(",") if id.strip().isdigit()]

# Описание режимов чата. Ключ - название режима, значение - системный промпт для OpenAI
CHAT_MODES = {
    "Помощник": "Ты — полезный ассистент.",
    "Шутник": "Ты — саркастичный и остроумный собеседник, который на всё отвечает шутками.",
    "Переводчик": "Ты — профессиональный переводчик. Переводи любой текст, который тебе присылают, на английский язык."
}

# Настройки системы кредитов
INITIAL_CREDITS = 7
MESSAGE_COST = 1
IMAGE_COST = 5

# --- НОВОЕ: Настройки голосовых сообщений ---
VOICE_TO_TEXT_COST = 2      # Стоимость распознавания речи
TEXT_TO_VOICE_COST = 3      # Стоимость синтеза речи
MAX_VOICE_DURATION = 300    # Максимальная длительность голосового сообщения (секунды)

# Доступные голоса для TTS (OpenAI поддерживает: alloy, echo, fable, onyx, nova, shimmer)
AVAILABLE_VOICES = {
    "🎭 Alloy": "alloy",           # Нейтральный
    "🔊 Echo": "echo",             # Мужской 
    "📖 Fable": "fable",           # Британский акцент
    "💎 Onyx": "onyx",             # Глубокий мужской
    "✨ Nova": "nova",             # Женский
    "🌟 Shimmer": "shimmer"        # Женский мягкий
}

# Доступные языки для распознавания речи
AVAILABLE_LANGUAGES = {
    "🇷🇺 Русский": "ru",
    "🇺🇸 English": "en", 
    "🇪🇸 Español": "es",
    "🇫🇷 Français": "fr",
    "🇩🇪 Deutsch": "de",
    "🇮🇹 Italiano": "it",
    "🇵🇹 Português": "pt",
    "🇯🇵 日本語": "ja",
    "🇰🇷 한국어": "ko",
    "🇨🇳 中文": "zh",
    "🇵🇱 Polski": "pl"
}

# Словарь доступных моделей
AVAILABLE_MODELS = {
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
    "GPT-4o (NEW)": "gpt-4o",
}

# --- Настройки реферальной программы ---
REFERRAL_BONUS_INVITER = 5  # Бонус тому, кто пригласил
REFERRAL_BONUS_NEW_USER = 2 # Бонус новому пользователю, который пришел по ссылке

# --- Настройки для реферальных кодов ---
REFERRAL_CODE_LENGTH = 8    # Длина уникальной части реферального кода

# --- Проверка обязательных переменных ---
required_vars = {
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_KEY": SUPABASE_KEY,
    "BOT_USERNAME": BOT_USERNAME,
}

missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]

if missing_vars:
    raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

print("✅ Конфигурация загружена успешно!")
print(f"🤖 Бот: @{BOT_USERNAME}")
print(f"👑 Админы: {ADMIN_USER_IDS}")
print(f"🔗 Supabase: {SUPABASE_URL[:30]}...")
print(f"🎙️ Голосовые сообщения: включены ({len(AVAILABLE_VOICES)} голосов)")