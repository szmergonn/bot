# handlers/common_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import db
from config import REFERRAL_BONUS_INVITER, REFERRAL_BONUS_NEW_USER
from translations import get_text

# ИСПРАВЛЕНО: Принимаем клиент supabase
def register_handlers(application, supabase):
    
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat_id = update.effective_chat.id
        user_language_code = user.language_code  # Получаем язык из Telegram
        
        # Проверяем, существует ли пользователь
        existing_user = await db.get_user_data(supabase, chat_id)
        
        # Проверяем, есть ли реферальный код в аргументах команды
        referral_code = None
        if context.args and len(context.args) > 0:
            referral_code = context.args[0]
        
        # Если пользователь новый и есть реферальный код
        if not existing_user and referral_code:
            await handle_new_user_with_referral(update, context, supabase, chat_id, referral_code, user, user_language_code)
        else:
            # Обычная обработка команды /start
            await db.add_or_update_user(supabase, chat_id, language_code=user_language_code)
            await db.clear_user_history(supabase, chat_id)
            
            # НОВОЕ: Синхронизируем голосовой язык с интерфейсом для новых пользователей
            if not existing_user and user_language_code:
                await db.sync_voice_language_with_interface(supabase, chat_id)
            
            # Получаем язык пользователя для переводов
            user_language = await db.get_user_language(supabase, chat_id)
            
            # Формируем приветственное сообщение на языке пользователя
            if existing_user:
                welcome_message = get_text(user_language, 'welcome_back', user=user.mention_html())
                welcome_message += "\n\n" + get_text(user_language, 'welcome_message', user=user.mention_html())
            else:
                welcome_message = get_text(user_language, 'welcome_message', user=user.mention_html())
            
            await update.message.reply_html(welcome_message)

    async def handle_new_user_with_referral(update, context, supabase, user_id, referral_code, user, user_language_code):
        """Обрабатывает нового пользователя, пришедшего по реферальной ссылке."""
        
        # Ищем пользователя, который пригласил
        inviter = await db.get_user_by_referral_code(supabase, referral_code)
        
        # Создаем пользователя с автоопределением языка
        await db.add_or_update_user(supabase, user_id, language_code=user_language_code)
        
        # НОВОЕ: Синхронизируем голосовой язык с интерфейсом
        await db.sync_voice_language_with_interface(supabase, user_id)
        
        user_language = await db.get_user_language(supabase, user_id)
        
        if not inviter:
            # Реферальный код недействителен
            await db.clear_user_history(supabase, user_id)
            welcome_message = get_text(user_language, 'referral_invalid_code', user=user.mention_html())
            await update.message.reply_html(welcome_message)
            return
        
        inviter_id = inviter['user_id']
        
        # Проверяем, что пользователь не использует свой собственный код
        if inviter_id == user_id:
            await db.clear_user_history(supabase, user_id)
            welcome_message = get_text(user_language, 'referral_own_code', user=user.mention_html())
            await update.message.reply_html(welcome_message)
            return
        
        # Обновляем пользователя с указанием, кто его пригласил
        await db.set_user_referral(supabase, user_id, inviter_id)
        await db.clear_user_history(supabase, user_id)
        
        # Начисляем бонусы
        success = await db.award_referral_bonuses(
            supabase, inviter_id, user_id, 
            REFERRAL_BONUS_INVITER, REFERRAL_BONUS_NEW_USER
        )
        
        if success:
            # Получаем новый баланс
            user_credits = await db.get_user_credits(supabase, user_id)
            
            # Уведомляем нового пользователя на его языке
            welcome_message = get_text(
                user_language, 'referral_welcome',
                user=user.mention_html(),
                bonus=REFERRAL_BONUS_NEW_USER,
                total=user_credits
            )
            await update.message.reply_html(welcome_message)
            
            # Уведомляем пригласившего пользователя на его языке
            try:
                inviter_language = await db.get_user_language(supabase, inviter_id)
                inviter_balance = await db.get_user_credits(supabase, inviter_id)
                
                notification_message = get_text(
                    inviter_language, 'referral_inviter_notification',
                    bonus=REFERRAL_BONUS_INVITER,
                    balance=inviter_balance
                )
                
                await context.bot.send_message(
                    chat_id=inviter_id,
                    text=notification_message
                )
            except Exception as e:
                print(f"Не удалось отправить уведомление пригласившему {inviter_id}: {e}")
        else:
            # Если не удалось начислить бонусы
            welcome_message = get_text(user_language, 'welcome_message', user=user.mention_html())
            await update.message.reply_html(welcome_message)

    async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        user_language = await db.get_user_language(supabase, chat_id)
        
        await db.clear_user_history(supabase, chat_id)
        
        message = get_text(user_language, 'new_dialog')
        await update.message.reply_text(message)

    async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        user_language = await db.get_user_language(supabase, chat_id)
        credits = await db.get_user_credits(supabase, chat_id)
        
        message = get_text(user_language, 'balance_info', credits=credits)
        await update.message.reply_text(message)

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("new", new_command))
    application.add_handler(CommandHandler("balance", balance_command))