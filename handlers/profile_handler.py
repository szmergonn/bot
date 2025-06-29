# handlers/profile_handler.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import db

def register_handlers(application, supabase):
    
    async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        bot_username = context.bot.username  # Получаем юзернейм бота динамически
        
        user_data = await db.get_user_data(supabase, user_id)
        
        if not user_data:
            await update.message.reply_text("❌ Не удалось найти ваш профиль. Попробуйте /start.")
            return
            
        credits = user_data.get('credits', 0)
        referral_code = user_data.get('referral_code', 'не найден')
        invited_by = user_data.get('invited_by')
        
        # Получаем статистику реферальной программы
        referral_stats = await db.get_referral_stats(supabase, user_id)
        invited_count = referral_stats.get('invited_count', 0)
        
        # Формируем реферальную ссылку
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        # Создаем текст профиля
        profile_text = f"👤 **Личный кабинет** - {user_name}\n\n"
        
        # Основная информация
        profile_text += f"**🆔 ID пользователя:** `{user_id}`\n"
        profile_text += f"**💰 Баланс:** {credits} кредитов\n\n"
        
        # Реферальная информация
        profile_text += f"🔗 **Реферальная программа:**\n"
        profile_text += f"📊 Приглашено друзей: **{invited_count}**\n"
        
        if invited_by:
            profile_text += f"👥 Вас пригласил: `{invited_by}`\n"
        
        profile_text += f"\n**Ваша реферальная ссылка:**\n`{referral_link}`\n\n"
        
        # Информация о бонусах
        profile_text += (
            "💡 **Как это работает:**\n"
            "• Поделитесь ссылкой с друзьями\n"
            "• Они получат +2 кредита при регистрации\n"
            "• Вы получите +5 кредитов за каждого друга\n\n"
            "🎯 Приглашайте больше друзей и получайте больше кредитов!"
        )
        
        await update.message.reply_text(profile_text, parse_mode='Markdown')

    application.add_handler(CommandHandler("profile", profile_command))