# handlers/common_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import db
from config import REFERRAL_BONUS_INVITER, REFERRAL_BONUS_NEW_USER

# ИСПРАВЛЕНО: Принимаем клиент supabase
def register_handlers(application, supabase):
    
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Проверяем, существует ли пользователь
        existing_user = await db.get_user_data(supabase, chat_id)
        
        # Проверяем, есть ли реферальный код в аргументах команды
        referral_code = None
        if context.args and len(context.args) > 0:
            referral_code = context.args[0]
        
        # Если пользователь новый и есть реферальный код
        if not existing_user and referral_code:
            await handle_new_user_with_referral(update, context, supabase, chat_id, referral_code, user)
        else:
            # Обычная обработка команды /start
            await db.add_or_update_user(supabase, chat_id)
            await db.clear_user_history(supabase, chat_id)
            
            welcome_message = (
                f"Привет, {user.mention_html()}! Я твой AI-ассистент.\n\n"
                f"Используй /menu, чтобы выбрать режим.\n"
                f"Используй /balance, чтобы проверить баланс кредитов.\n"
                f"Используй /profile, чтобы открыть личный кабинет."
            )
            
            if existing_user:
                welcome_message = f"С возвращением, {user.mention_html()}!\n\n" + welcome_message
            
            await update.message.reply_html(welcome_message)

    async def handle_new_user_with_referral(update, context, supabase, user_id, referral_code, user):
        """Обрабатывает нового пользователя, пришедшего по реферальной ссылке."""
        
        # Ищем пользователя, который пригласил
        inviter = await db.get_user_by_referral_code(supabase, referral_code)
        
        if not inviter:
            # Реферальный код недействителен
            await db.add_or_update_user(supabase, user_id)
            await update.message.reply_html(
                f"Привет, {user.mention_html()}! Я твой AI-ассистент.\n\n"
                f"Реферальный код недействителен, но вы всё равно получили стартовые кредиты!\n\n"
                f"Используй /menu, чтобы выбрать режим.\n"
                f"Используй /profile, чтобы открыть личный кабинет."
            )
            return
        
        inviter_id = inviter['user_id']
        
        # Проверяем, что пользователь не использует свой собственный код
        if inviter_id == user_id:
            await db.add_or_update_user(supabase, user_id)
            await update.message.reply_html(
                f"Привет, {user.mention_html()}! Я твой AI-ассистент.\n\n"
                f"Нельзя использовать собственный реферальный код 😊\n\n"
                f"Используй /menu, чтобы выбрать режим.\n"
                f"Используй /profile, чтобы открыть личный кабинет."
            )
            return
        
        # Создаем нового пользователя с указанием, кто его пригласил
        await db.add_or_update_user(supabase, user_id, invited_by=inviter_id)
        await db.clear_user_history(supabase, user_id)
        
        # Начисляем бонусы
        success = await db.award_referral_bonuses(
            supabase, inviter_id, user_id, 
            REFERRAL_BONUS_INVITER, REFERRAL_BONUS_NEW_USER
        )
        
        if success:
            # Уведомляем нового пользователя
            await update.message.reply_html(
                f"🎉 Добро пожаловать, {user.mention_html()}!\n\n"
                f"Вы пришли по реферальной ссылке и получили бонус {REFERRAL_BONUS_NEW_USER} кредитов!\n"
                f"Всего у вас теперь кредитов: {await db.get_user_credits(supabase, user_id)}\n\n"
                f"Используйте /menu для начала работы и /profile для личного кабинета."
            )
            
            # Уведомляем пригласившего пользователя
            try:
                await context.bot.send_message(
                    chat_id=inviter_id,
                    text=(
                        f"🎉 Отличные новости!\n\n"
                        f"По вашей реферальной ссылке зарегистрировался новый пользователь!\n"
                        f"Вы получили бонус {REFERRAL_BONUS_INVITER} кредитов.\n\n"
                        f"Ваш баланс: {await db.get_user_credits(supabase, inviter_id)} кредитов"
                    )
                )
            except Exception as e:
                print(f"Не удалось отправить уведомление пригласившему {inviter_id}: {e}")
        else:
            # Если не удалось начислить бонусы
            await update.message.reply_html(
                f"Привет, {user.mention_html()}! Я твой AI-ассистент.\n\n"
                f"Добро пожаловать! Используйте /menu для начала работы."
            )

    async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        await db.clear_user_history(supabase, chat_id)
        await update.message.reply_text("Отлично, начинаем новый диалог в текущем режиме!")

    async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        credits = await db.get_user_credits(supabase, chat_id)
        await update.message.reply_text(f"💰 У вас на балансе: {credits} кредитов.")

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("new", new_command))
    application.add_handler(CommandHandler("balance", balance_command))