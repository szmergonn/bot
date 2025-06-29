# database/db.py

import secrets
import string
from config import INITIAL_CREDITS, AVAILABLE_MODELS, REFERRAL_CODE_LENGTH

# --- Функции для работы с БД. Каждая принимает 'supabase' клиент как первый аргумент ---

DEFAULT_MODEL = list(AVAILABLE_MODELS.values())[0]

def generate_referral_code(user_id):
    """Генерирует уникальный реферальный код для пользователя."""
    # Создаем код из префикса + user_id + случайная строка
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(REFERRAL_CODE_LENGTH))
    return f"ref{user_id}_{random_part}"

async def add_or_update_user(supabase, user_id, invited_by=None):
    """Добавляет нового пользователя с реферальным кодом, если его нет."""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await get_user_data(supabase, user_id)
        if existing_user:
            return existing_user
            
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
            "referral_code": referral_code
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
    """Получает все данные пользователя включая реферальную информацию."""
    try:
        response = await supabase.table("users").select(
            "state, mode, credits, model, referral_code, invited_by, created_at"
        ).eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Ошибка при получении данных пользователя {user_id}: {e}")
    return None

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
        # Начисляем бонус пригласившему
        await add_user_credits(supabase, inviter_id, inviter_bonus)
        
        # Начисляем бонус новому пользователю
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
        # Количество приглашенных пользователей
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