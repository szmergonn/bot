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

# ОБНОВЛЕНО: Многоязычные режимы чата с системными промптами на разных языках
CHAT_MODES = {
    "Помощник": {
        "ru": "Ты — полезный ассистент. Отвечай на русском языке четко и информативно.",
        "en": "You are a helpful assistant. Respond in English clearly and informatively.", 
        "pl": "Jesteś pomocnym asystentem. Odpowiadaj po polsku jasno i informatywnie."
    },
    "Шутник": {
        "ru": "Ты — саркастичный и остроумный собеседник, который на всё отвечает шутками. Отвечай на русском языке.",
        "en": "You are a sarcastic and witty conversationalist who responds to everything with jokes. Respond in English.",
        "pl": "Jesteś sarkastycznym i dowcipnym rozmówcą, który na wszystko odpowiada żartami. Odpowiadaj po polsku."
    },
    "Переводчик": {
        "ru": "Ты — профессиональный переводчик. Переводи любой текст, который тебе присылают, на английский язык. Если текст уже на английском, переведи его на русский.",
        "en": "You are a professional translator. Translate any text sent to you into Russian. If the text is already in Russian, translate it to English.",
        "pl": "Jesteś profesjonalnym tłumaczem. Tłumacz każdy tekst, który ci wysyłają, na angielski. Jeśli tekst jest już po angielsku, przetłumacz go na polski."
    }
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

# Доступные языки для распознавания речи (только 3 основных)
AVAILABLE_LANGUAGES = {
    "🇷🇺 Русский": "ru",
    "🇺🇸 English": "en", 
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

# НОВОЕ: Функция для получения системного промпта на нужном языке
def get_system_prompt(mode_name: str, language: str) -> str:
    """
    Получает системный промпт для режима на указанном языке.
    
    Args:
        mode_name: Название режима ('Помощник', 'Шутник', 'Переводчик')
        language: Код языка ('ru', 'en', 'pl')
    
    Returns:
        Системный промпт на нужном языке
    """
    if mode_name in CHAT_MODES and language in CHAT_MODES[mode_name]:
        return CHAT_MODES[mode_name][language]
    
    # Fallback на английский, если язык не найден
    if mode_name in CHAT_MODES and 'en' in CHAT_MODES[mode_name]:
        return CHAT_MODES[mode_name]['en']
    
    # Последний fallback
    return "You are a helpful assistant."

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
print(f"🌍 Многоязычность: {len(CHAT_MODES)} режимов на {len(list(CHAT_MODES.values())[0])} языках")
print(f"🗣️ Голосовое распознавание: {len(AVAILABLE_LANGUAGES)} языка")