# handlers/admin_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from functools import wraps
import asyncio
from config import ADMIN_USER_IDS
from database import db

# ИСПРАВЛЕНО: Принимаем supabase
def register_handlers(application, supabase):

    def admin_only(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id not in ADMIN_USER_IDS:
                await update.message.reply_text("Эта команда доступна только администратору.")
                return
            return await func(update, context, *args, **kwargs)
        return wrapped

    @admin_only
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Добро пожаловать в админ-панель!\n\n"
            "Доступные команды:\n"
            "/stats - Показать статистику\n"
            "/broadcast <сообщение> - Отправить сообщение всем пользователям\n"
            "/add_credits <user_id> <количество> - Начислить кредиты пользователю"
        )

    @admin_only
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_count = await db.count_users(supabase)
        await update.message.reply_text(f"Всего пользователей в боте: {user_count}")

    @admin_only
    async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_to_send = " ".join(context.args)
        if not message_to_send:
            await update.message.reply_text("Укажите сообщение. Пример: /broadcast Привет!")
            return
        user_ids = await db.get_all_user_ids(supabase)
        await update.message.reply_text(f"Начинаю рассылку для {len(user_ids)} пользователей...")
        success_count, fail_count = 0, 0
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text=message_to_send)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                fail_count += 1
                print(f"Не удалось отправить сообщение {user_id}: {e}")
        await update.message.reply_text(f"Рассылка завершена! Успешно: {success_count}, Ошибок: {fail_count}")

    @admin_only
    async def add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = int(context.args[0])
            amount = int(context.args[1])
            await db.add_user_credits(supabase, user_id, amount)
            new_balance = await db.get_user_credits(supabase, user_id)
            await update.message.reply_text(f"Пользователю {user_id} начислено {amount} кредитов. Новый баланс: {new_balance}.")
            try:
                await context.bot.send_message(chat_id=user_id, text=f"Вам было начислено {amount} кредитов!")
            except Exception:
                await update.message.reply_text("(Не удалось уведомить пользователя)")
        except (IndexError, ValueError):
            await update.message.reply_text("Неверный формат. Используйте: /add_credits <user_id> <сумма>")

    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("add_credits", add_credits_command))