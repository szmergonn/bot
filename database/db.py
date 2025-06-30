# database/db.py

import secrets
import string
from config import INITIAL_CREDITS, AVAILABLE_MODELS, REFERRAL_CODE_LENGTH, AVAILABLE_VOICES

# --- Функции для работы с БД. Каждая принимает 'supabase' клиент как первый аргумент ---

DEFAULT_MODEL = list(AVAILABLE_MODELS.values())[0]
DEFAULT_VOICE = list(AVAILABLE_VOICES.values())[0]

def generate_referral_code(user_id):
    """Генерирует уникальный реферальный код для пользователя."""
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(REFERRAL_CODE_LENGTH))
    return f"ref{user_id}_{random_part}"

async def add_or_update_user(supabase, user_id, invited_by=None, language_code=None):
    """Добавляет нового пользователя с реферальным кодом и настройками голоса, если его нет."""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await get_user_data(supabase, user_id)
        if existing_user:
            return existing_user
            
        # Определяем язык интерфейса
        from translations import detect_user_language
        interface_language = detect_user_language(language_code) if language_code else 'en'
        
        # НОВОЕ: Устанавливаем голосовой язык таким же как интерфейс
        voice_language = interface_language  # ru/en/pl
        
        print(f"🌍 Новый пользователь {user_id}: интерфейс={interface_language}, голосовой={voice_language}")
            
        # Генерируем уникальный реферальный код
        referral_code = generate_referral_code(user_id)
        
        # Убеждаемся, что код уникален
        max_attempts = 5
        for _ in range(max_attempts):
            existing_code = await get_user_by_referral_code(supabase, referral_code)
            if not existing_code:
                break
            referral_code = generate_referral_code(user_id)
        
        user_data = {
            "user_id": user_id, 
            "credits": INITIAL_CREDITS, 
            "model": DEFAULT_MODEL,
            "referral_code": referral_code,
            "selected_voice": DEFAULT_VOICE,
            "voice_enabled": False,
            "voice_language": voice_language,  # ИСПРАВЛЕНО: используем интерфейсный язык
            "interface_language": interface_language,
            "streaming_enabled": True  # По умолчанию включаем streaming
        }
        
        # Добавляем информацию о том, кто пригласил, если есть
        if invited_by:
            user_data["invited_by"] = invited_by
            
        await supabase.table("users").insert(user_data).execute()
        return await get_user_data(supabase, user_id)
        
    except Exception as e:
        print(f"Ошибка при добавлении пользователя {user_id}: {e}")
        return None

async def get_user_data(supabase, user_id):
    """Получает все данные пользователя включая голосовые настройки, язык интерфейса и streaming."""
    try:
        response = await supabase.table("users").select(
            "state, mode, credits, model, referral_code, invited_by, created_at, "
            "voice_enabled, selected_voice, voice_language, voice_messages_sent, voice_messages_received, "
            "interface_language, streaming_enabled"
        ).eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Ошибка при получении данных пользователя {user_id}: {e}")
    return None

# --- НОВЫЕ ФУНКЦИИ ДЛЯ ГОЛОСОВЫХ СООБЩЕНИЙ ---

# --- НОВЫЕ ФУНКЦИИ ДЛЯ ЯЗЫКА ИНТЕРФЕЙСА ---

async def get_user_language(supabase, user_id):
    """Получает язык интерфейса пользователя."""
    try:
        response = await supabase.table("users").select("interface_language").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0].get('interface_language', 'en')
    except Exception as e:
        print(f"Ошибка при получении языка пользователя {user_id}: {e}")
    return 'en'

async def set_user_language(supabase, user_id, language_code):
    """Устанавливает язык интерфейса для пользователя."""
    allowed_languages = ['ru', 'en', 'pl']
    if language_code in allowed_languages:
        try:
            await supabase.table("users").update({"interface_language": language_code}).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Ошибка при установке языка интерфейса для {user_id}: {e}")
    return False

async def set_user_language_with_voice_sync(supabase, user_id, language_code):
    """
    Устанавливает язык интерфейса и автоматически синхронизирует язык голосового общения.
    """
    allowed_languages = ['ru', 'en', 'pl']
    if language_code in allowed_languages:
        try:
            # ОБНОВЛЕНО: Всегда синхронизируем голосовой язык с интерфейсным
            voice_language = language_code  # ru->ru, en->en, pl->pl
            
            # Обновляем оба языка одновременно
            await supabase.table("users").update({
                "interface_language": language_code,
                "voice_language": voice_language
            }).eq("user_id", user_id).execute()
            
            print(f"🔄 Пользователь {user_id}: интерфейс={language_code}, голосовой={voice_language} (синхронизированы)")
            return True
        except Exception as e:
            print(f"Ошибка при синхронизации языков для {user_id}: {e}")
    return False

async def sync_voice_language_with_interface(supabase, user_id):
    """
    Синхронизирует язык голосового общения с текущим языком интерфейса.
    Теперь всегда: ru->ru, en->en, pl->pl
    """
    try:
        # Получаем текущий язык интерфейса
        interface_language = await get_user_language(supabase, user_id)
        
        # УПРОЩЕНО: Голосовой язык = интерфейсному языку
        voice_language = interface_language  # ru->ru, en->en, pl->pl
        
        # Обновляем язык голосового общения
        await supabase.table("users").update({
            "voice_language": voice_language
        }).eq("user_id", user_id).execute()
        
        print(f"🔄 Синхронизация {user_id}: {interface_language} -> {voice_language}")
        return True
    except Exception as e:
        print(f"Ошибка при синхронизации голосового языка для {user_id}: {e}")
        return False

async def set_user_referral(supabase, user_id, inviter_id):
    """Устанавливает, кто пригласил пользователя."""
    try:
        await supabase.table("users").update({"invited_by": inviter_id}).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Ошибка при установке пригласившего для {user_id}: {e}")
        return False

async def get_user_voice_settings(supabase, user_id):
    """Получает голосовые настройки пользователя."""
    try:
        response = await supabase.table("users").select(
            "voice_enabled, selected_voice, voice_language"
        ).eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Ошибка при получении голосовых настроек {user_id}: {e}")
    return {"voice_enabled": False, "selected_voice": DEFAULT_VOICE, "voice_language": "ru"}

async def set_voice_enabled(supabase, user_id, enabled):
    """Включает или выключает голосовые ответы для пользователя."""
    try:
        await supabase.table("users").update({"voice_enabled": enabled}).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Ошибка при изменении voice_enabled для {user_id}: {e}")
        return False

async def set_user_voice(supabase, user_id, voice_id):
    """Устанавливает выбранный голос для пользователя."""
    if voice_id in AVAILABLE_VOICES.values():
        try:
            await supabase.table("users").update({"selected_voice": voice_id}).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Ошибка при установке голоса для {user_id}: {e}")
    return False

async def set_user_voice_language(supabase, user_id, language):
    """Устанавливает язык распознавания речи для пользователя (только 3 основных языка)."""
    allowed_languages = ['ru', 'en', 'pl']  # Только 3 языка
    if language in allowed_languages:
        try:
            await supabase.table("users").update({"voice_language": language}).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Ошибка при установке языка голоса для {user_id}: {e}")
    return False

async def increment_voice_stats(supabase, user_id, message_type):
    """Увеличивает счетчик отправленных или полученных голосовых сообщений."""
    try:
        # Получаем текущие значения
        current_data = await get_user_data(supabase, user_id)
        if not current_data:
            return
            
        if message_type == "sent":
            current_count = current_data.get("voice_messages_sent", 0)
            await supabase.table("users").update({
                "voice_messages_sent": current_count + 1
            }).eq("user_id", user_id).execute()
        elif message_type == "received":
            current_count = current_data.get("voice_messages_received", 0)
            await supabase.table("users").update({
                "voice_messages_received": current_count + 1
            }).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Ошибка при обновлении статистики голосовых для {user_id}: {e}")

async def get_voice_stats(supabase, user_id):
    """Получает статистику использования голосовых сообщений."""
    try:
        response = await supabase.table("users").select(
            "voice_messages_sent, voice_messages_received"
        ).eq("user_id", user_id).execute()
        if response.data:
            data = response.data[0]
            return {
                "sent": data.get("voice_messages_sent", 0),
                "received": data.get("voice_messages_received", 0)
            }
    except Exception as e:
        print(f"Ошибка при получении статистики голосовых для {user_id}: {e}")
    return {"sent": 0, "received": 0}

# --- НОВЫЕ ФУНКЦИИ ДЛЯ STREAMING RESPONSE ---

async def get_user_streaming_setting(supabase, user_id):
    """Получает настройку streaming для пользователя."""
    try:
        response = await supabase.table("users").select("streaming_enabled").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0].get('streaming_enabled', True)
    except Exception as e:
        print(f"Ошибка при получении настройки streaming для {user_id}: {e}")
    return True  # По умолчанию включен

async def set_user_streaming(supabase, user_id, enabled):
    """Включает или выключает streaming response для пользователя."""
    try:
        await supabase.table("users").update({"streaming_enabled": enabled}).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Ошибка при изменении streaming для {user_id}: {e}")
        return False

# --- СУЩЕСТВУЮЩИЕ ФУНКЦИИ (без изменений) ---

async def get_user_by_referral_code(supabase, referral_code):
    """Находит пользователя по реферальному коду."""
    try:
        response = await supabase.table("users").select(
            "user_id, referral_code"
        ).eq("referral_code", referral_code).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Ошибка при поиске пользователя по коду {referral_code}: {e}")
    return None

async def award_referral_bonuses(supabase, inviter_id, new_user_id, inviter_bonus, new_user_bonus):
    """Начисляет бонусы за реферальную программу."""
    try:
        await add_user_credits(supabase, inviter_id, inviter_bonus)
        await add_user_credits(supabase, new_user_id, new_user_bonus)
        return True
    except Exception as e:
        print(f"Ошибка при начислении реферальных бонусов: {e}")
        return False

async def get_user_credits(supabase, user_id):
    """Получает баланс кредитов пользователя."""
    data = await get_user_data(supabase, user_id)
    return data['credits'] if data else 0

async def deduct_user_credits(supabase, user_id, amount):
    """Списывает кредиты с баланса пользователя."""
    current_credits = await get_user_credits(supabase, user_id)
    new_credits = max(0, current_credits - amount)
    try:
        await supabase.table("users").update({"credits": new_credits}).eq("user_id", user_id).execute()
        return new_credits
    except Exception as e:
        print(f"Ошибка при списании кредитов у {user_id}: {e}")
    return current_credits

async def add_user_credits(supabase, user_id, amount):
    """Начисляет кредиты пользователю."""
    current_credits = await get_user_credits(supabase, user_id)
    new_credits = current_credits + amount
    try:
        await supabase.table("users").update({"credits": new_credits}).eq("user_id", user_id).execute()
        return new_credits
    except Exception as e:
        print(f"Ошибка при начислении кредитов {user_id}: {e}")
    return current_credits

async def remove_user_credits(supabase, user_id, amount, allow_negative=False):
    """Снимает кредиты у пользователя.
    
    Args:
        supabase: клиент базы данных
        user_id: ID пользователя
        amount: количество кредитов для снятия (положительное число)
        allow_negative: разрешить уход в минус (по умолчанию False)
    
    Returns:
        tuple: (новый_баланс, успешно_ли_операция)
    """
    current_credits = await get_user_credits(supabase, user_id)
    
    if not allow_negative and current_credits < amount:
        # Не можем снять больше, чем есть
        return current_credits, False
    
    new_credits = current_credits - amount
    
    try:
        await supabase.table("users").update({"credits": new_credits}).eq("user_id", user_id).execute()
        return new_credits, True
    except Exception as e:
        print(f"Ошибка при снятии кредитов у {user_id}: {e}")
        return current_credits, False

async def get_all_user_ids(supabase):
    """Возвращает список ID всех пользователей."""
    try:
        response = await supabase.table("users").select("user_id").execute()
        return [item['user_id'] for item in response.data]
    except Exception as e:
        print(f"Ошибка при получении всех ID пользователей: {e}")
    return []

async def count_users(supabase):
    """Считает общее количество пользователей."""
    try:
        response = await supabase.table("users").select("user_id", count='exact').execute()
        return response.count
    except Exception as e:
        print(f"Ошибка при подсчете пользователей: {e}")
    return 0

async def get_referral_stats(supabase, user_id):
    """Получает статистику реферальной программы для пользователя."""
    try:
        response = await supabase.table("users").select("user_id", count='exact').eq("invited_by", user_id).execute()
        invited_count = response.count or 0
        return {"invited_count": invited_count}
    except Exception as e:
        print(f"Ошибка при получении реферальной статистики для {user_id}: {e}")
    return {"invited_count": 0}

async def set_user_state(supabase, user_id, state):
    """Устанавливает состояние пользователя."""
    try:
        await supabase.table("users").update({"state": state}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Ошибка при установке состояния для {user_id}: {e}")

async def set_user_mode(supabase, user_id, mode):
    """Устанавливает режим и сбрасывает историю."""
    try:
        await supabase.table("users").update({"mode": mode, "state": 'chat'}).eq("user_id", user_id).execute()
        await clear_user_history(supabase, user_id)
    except Exception as e:
        print(f"Ошибка при установке режима для {user_id}: {e}")

async def set_user_model(supabase, user_id, model_id):
    """Устанавливает выбранную модель для пользователя."""
    if model_id in AVAILABLE_MODELS.values():
        try:
            await supabase.table("users").update({"model": model_id}).eq("user_id", user_id).execute()
        except Exception as e:
            print(f"Ошибка при установке модели для {user_id}: {e}")

async def get_user_history(supabase, user_id, limit=10):
    """Получает историю сообщений пользователя."""
    try:
        response = await supabase.table("messages").select("role, content").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return list(reversed(response.data))
    except Exception as e:
        print(f"Ошибка при получении истории для {user_id}: {e}")
    return []

async def add_message_to_history(supabase, user_id, role, content):
    """Добавляет сообщение в историю."""
    try:
        await supabase.table("messages").insert({"user_id": user_id, "role": role, "content": content}).execute()
    except Exception as e:
        print(f"Ошибка при добавлении сообщения в историю для {user_id}: {e}")

async def clear_user_history(supabase, user_id):
    """Очищает историю сообщений пользователя."""
    try:
        await supabase.table("messages").delete().eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Ошибка при очистке истории для {user_id}: {e}")