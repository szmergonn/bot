# handlers/profile_handler.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import db
from translations import get_text

def register_handlers(application, supabase):
    
    async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        bot_username = context.bot.username  # Получаем юзернейм бота динамически
        
        # Получаем язык пользователя
        user_language = await db.get_user_language(supabase, user_id)
        
        user_data = await db.get_user_data(supabase, user_id)
        
        if not user_data:
            error_message = get_text(user_language, 'profile_not_found')
            await update.message.reply_text(error_message)
            return
            
        credits = user_data.get('credits', 0)
        referral_code = user_data.get('referral_code', 'не найден')
        invited_by = user_data.get('invited_by')
        
        # Получаем статистику реферальной программы
        referral_stats = await db.get_referral_stats(supabase, user_id)
        invited_count = referral_stats.get('invited_count', 0)
        
        # Формируем реферальную ссылку
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        # Создаем текст профиля на языке пользователя
        profile_text = get_text(user_language, 'profile_title', name=user_name) + "\n\n"
        
        # Основная информация
        profile_text += get_text(user_language, 'profile_user_id', user_id=user_id) + "\n"
        profile_text += get_text(user_language, 'profile_balance', credits=credits) + "\n\n"
        
        # Реферальная информация
        profile_text += get_text(user_language, 'profile_referral_program') + "\n"
        profile_text += get_text(user_language, 'profile_invited_friends', count=invited_count) + "\n"
        
        if invited_by:
            profile_text += get_text(user_language, 'profile_invited_by', user_id=invited_by) + "\n"
        
        profile_text += "\n" + get_text(user_language, 'profile_referral_link', link=referral_link) + "\n\n"
        
        # Информация о том, как работает система
        profile_text += get_text(user_language, 'profile_how_it_works')
        
        await update.message.reply_text(profile_text, parse_mode='Markdown')

    application.add_handler(CommandHandler("profile", profile_command))