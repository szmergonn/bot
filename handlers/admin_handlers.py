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
            "👑 **Добро пожаловать в админ-панель!**\n\n"
            "📊 **Статистика:**\n"
            "/stats - Показать статистику бота\n"
            "/user\\_info <user\\_id> - Подробная информация о пользователе\n\n"
            "💰 **Управление кредитами:**\n"
            "/add\\_credits <user\\_id> <количество> - Начислить кредиты\n"
            "/remove\\_credits <user\\_id> <количество> - Снять кредиты\n\n"
            "📢 **Рассылка:**\n"
            "/broadcast <сообщение> - Отправить всем пользователям\n\n"
            "ℹ️ Используйте команды для управления ботом.",
            parse_mode='Markdown'
        )

    @admin_only
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Получаем общую статистику
            user_count = await db.count_users(supabase)
            
            # Получаем дополнительную статистику
            all_users = await db.get_all_user_ids(supabase)
            
            total_credits = 0
            voice_enabled_count = 0
            negative_balance_count = 0
            
            for user_id in all_users:
                user_data = await db.get_user_data(supabase, user_id)
                if user_data:
                    credits = user_data.get('credits', 0)
                    total_credits += credits
                    
                    if credits < 0:
                        negative_balance_count += 1
                    
                    if user_data.get('voice_enabled', False):
                        voice_enabled_count += 1
            
            # Вычисляем средний баланс
            avg_credits = round(total_credits / user_count, 2) if user_count > 0 else 0
            
            stats_message = (
                f"📊 **Статистика бота**\n\n"
                f"👥 **Пользователи:**\n"
                f"• Всего пользователей: **{user_count}**\n"
                f"• С голосовыми ответами: **{voice_enabled_count}**\n"
                f"• С отрицательным балансом: **{negative_balance_count}**\n\n"
                f"💰 **Кредиты:**\n"
                f"• Общий объем кредитов: **{total_credits}**\n"
                f"• Средний баланс: **{avg_credits}** кредитов\n\n"
                f"🎙️ **Голосовые сообщения:**\n"
                f"• Включили голосовые ответы: **{voice_enabled_count}** из {user_count} ({round(voice_enabled_count/user_count*100, 1) if user_count > 0 else 0}%)"
            )
            
            if negative_balance_count > 0:
                stats_message += f"\n\n⚠️ **Внимание:** {negative_balance_count} пользователей с отрицательным балансом!"
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при получении статистики: {e}")

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
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ **Неверный формат команды**\n\n"
                    "Используйте: `/add_credits <user_id> <количество>`\n\n"
                    "**Пример:** `/add_credits 123456789 10`",
                    parse_mode='Markdown'
                )
                return
                
            user_id = int(context.args[0])
            amount = int(context.args[1])
            
            if amount <= 0:
                await update.message.reply_text("❌ Количество кредитов должно быть положительным числом.")
                return
            
            # Получаем текущий баланс пользователя
            current_balance = await db.get_user_credits(supabase, user_id)
            
            # Проверяем, существует ли пользователь
            user_data = await db.get_user_data(supabase, user_id)
            if not user_data:
                await update.message.reply_text(f"❌ Пользователь с ID {user_id} не найден в базе данных.")
                return
            
            # Начисляем кредиты
            new_balance = await db.add_user_credits(supabase, user_id, amount)
            
            # Формируем сообщение админу
            admin_message = (
                f"✅ **Кредиты успешно начислены!**\n\n"
                f"👤 **Пользователь:** `{user_id}`\n"
                f"➕ **Начислено:** {amount} кредитов\n"
                f"💰 **Было:** {current_balance} кредитов\n"
                f"💰 **Стало:** {new_balance} кредитов"
            )
            
            await update.message.reply_text(admin_message, parse_mode='Markdown')
            
            # Уведомляем пользователя о начислении кредитов
            try:
                user_message = (
                    f"🎉 **Поздравляем!**\n\n"
                    f"Вам было начислено **{amount} кредитов** администратором!\n\n"
                    f"💰 **Текущий баланс:** {new_balance} кредитов"
                )
                
                await context.bot.send_message(chat_id=user_id, text=user_message, parse_mode='Markdown')
                
            except Exception as e:
                await update.message.reply_text(f"⚠️ Кредиты начислены, но не удалось уведомить пользователя: {e}")
                
        except (IndexError, ValueError):
            await update.message.reply_text(
                "❌ **Неверный формат команды**\n\n"
                "Используйте: `/add_credits <user_id> <количество>`\n\n"
                "**Пример:** `/add_credits 123456789 10`",
                parse_mode='Markdown'
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Произошла ошибка: {e}")

    @admin_only
    async def remove_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ **Неверный формат команды**\n\n"
                    "Используйте: `/remove_credits <user_id> <количество>`\n\n"
                    "**Примеры:**\n"
                    "• `/remove_credits 123456789 5` - снять 5 кредитов\n"
                    "• `/remove_credits 123456789 10 force` - снять 10 кредитов (даже если уйдет в минус)",
                    parse_mode='Markdown'
                )
                return
                
            user_id = int(context.args[0])
            amount = int(context.args[1])
            
            if amount <= 0:
                await update.message.reply_text("❌ Количество кредитов должно быть положительным числом.")
                return
            
            # Проверяем, есть ли флаг "force" для разрешения ухода в минус
            allow_negative = len(context.args) > 2 and context.args[2].lower() == "force"
            
            # Получаем текущий баланс пользователя
            current_balance = await db.get_user_credits(supabase, user_id)
            
            # Проверяем, существует ли пользователь
            user_data = await db.get_user_data(supabase, user_id)
            if not user_data:
                await update.message.reply_text(f"❌ Пользователь с ID {user_id} не найден в базе данных.")
                return
            
            # Снимаем кредиты
            new_balance, success = await db.remove_user_credits(supabase, user_id, amount, allow_negative)
            
            if success:
                # Формируем сообщение админу
                admin_message = (
                    f"✅ **Кредиты успешно сняты!**\n\n"
                    f"👤 **Пользователь:** `{user_id}`\n"
                    f"➖ **Снято:** {amount} кредитов\n"
                    f"💰 **Было:** {current_balance} кредитов\n"
                    f"💰 **Стало:** {new_balance} кредитов"
                )
                
                if new_balance < 0:
                    admin_message += f"\n\n⚠️ **Внимание:** Баланс пользователя ушел в минус!"
                
                await update.message.reply_text(admin_message, parse_mode='Markdown')
                
                # Уведомляем пользователя о снятии кредитов
                try:
                    user_message = (
                        f"📉 **Изменение баланса**\n\n"
                        f"С вашего счета было снято **{amount} кредитов** администратором.\n\n"
                        f"💰 **Текущий баланс:** {new_balance} кредитов"
                    )
                    
                    if new_balance < 0:
                        user_message += f"\n\n⚠️ Ваш баланс ушел в минус. Обратитесь к администратору."
                    
                    await context.bot.send_message(chat_id=user_id, text=user_message, parse_mode='Markdown')
                    
                except Exception as e:
                    await update.message.reply_text(f"⚠️ Кредиты сняты, но не удалось уведомить пользователя: {e}")
            else:
                # Не удалось снять кредиты
                await update.message.reply_text(
                    f"❌ **Не удалось снять кредиты**\n\n"
                    f"👤 **Пользователь:** `{user_id}`\n"
                    f"💰 **Текущий баланс:** {current_balance} кредитов\n"
                    f"➖ **Попытка снять:** {amount} кредитов\n\n"
                    f"💡 **Причина:** Недостаточно кредитов для снятия.\n"
                    f"Используйте `force` для принудительного снятия:\n"
                    f"`/remove_credits {user_id} {amount} force`",
                    parse_mode='Markdown'
                )
                
        except (IndexError, ValueError):
            await update.message.reply_text(
                "❌ **Неверный формат команды**\n\n"
                "Используйте: `/remove_credits <user_id> <количество> [force]`\n\n"
                "**Примеры:**\n"
                "• `/remove_credits 123456789 5`\n"
                "• `/remove_credits 123456789 10 force`",
                parse_mode='Markdown'
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Произошла ошибка: {e}")

    @admin_only
    async def user_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if len(context.args) < 1:
                await update.message.reply_text(
                    "❌ **Неверный формат команды**\n\n"
                    "Используйте: `/user_info <user_id>`\n\n"
                    "**Пример:** `/user_info 123456789`",
                    parse_mode='Markdown'
                )
                return
                
            user_id = int(context.args[0])
            
            # Получаем данные пользователя
            user_data = await db.get_user_data(supabase, user_id)
            
            if not user_data:
                await update.message.reply_text(f"❌ Пользователь с ID `{user_id}` не найден в базе данных.", parse_mode='Markdown')
                return
            
            # Получаем реферальную статистику
            referral_stats = await db.get_referral_stats(supabase, user_id)
            voice_stats = await db.get_voice_stats(supabase, user_id)
            
            # Формируем подробную информацию
            credits = user_data.get('credits', 0)
            mode = user_data.get('mode', 'Не установлен')
            model = user_data.get('model', 'Не установлен')
            state = user_data.get('state', 'chat')
            created_at = user_data.get('created_at', 'Неизвестно')
            
            # Голосовые настройки
            voice_enabled = user_data.get('voice_enabled', False)
            selected_voice = user_data.get('selected_voice', 'alloy')
            voice_language = user_data.get('voice_language', 'ru')
            
            # Реферальная информация
            referral_code = user_data.get('referral_code', 'Нет')
            invited_by = user_data.get('invited_by', 'Нет')
            invited_count = referral_stats.get('invited_count', 0)
            
            user_info_message = (
                f"👤 **Информация о пользователе**\n\n"
                f"**🆔 ID:** `{user_id}`\n"
                f"**📅 Регистрация:** {created_at}\n"
                f"**⚡ Состояние:** {state}\n\n"
                f"💰 **Баланс:** {credits} кредитов"
            )
            
            if credits < 0:
                user_info_message += " ⚠️"
            
            user_info_message += (
                f"\n\n🤖 **Настройки AI:**\n"
                f"• Режим: {mode}\n"
                f"• Модель: {model}\n\n"
                f"🎙️ **Голосовые сообщения:**\n"
                f"• Включены: {'Да' if voice_enabled else 'Нет'}\n"
                f"• Голос: {selected_voice}\n"
                f"• Язык: {voice_language.upper()}\n"
                f"• Отправлено: {voice_stats['sent']}\n"
                f"• Получено: {voice_stats['received']}\n\n"
                f"🔗 **Реферальная программа:**\n"
                f"• Код: `{referral_code}`\n"
                f"• Пригласил: {invited_by if invited_by != 'Нет' else 'Сам зарегистрировался'}\n"
                f"• Приглашено друзей: {invited_count}"
            )
            
            await update.message.reply_text(user_info_message, parse_mode='Markdown')
            
        except (IndexError, ValueError):
            await update.message.reply_text(
                "❌ **Неверный формат команды**\n\n"
                "Используйте: `/user_info <user_id>`\n\n"
                "**Пример:** `/user_info 123456789`",
                parse_mode='Markdown'
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Произошла ошибка: {e}")

    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("add_credits", add_credits_command))
    application.add_handler(CommandHandler("remove_credits", remove_credits_command))
    application.add_handler(CommandHandler("user_info", user_info_command))