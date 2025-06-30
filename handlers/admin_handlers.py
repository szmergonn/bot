# handlers/admin_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from functools import wraps
import asyncio
from config import ADMIN_USER_IDS
from database import db
from translations import get_text

# ИСПРАВЛЕНО: Принимаем supabase
def register_handlers(application, supabase):

    def admin_only(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id not in ADMIN_USER_IDS:
                # Получаем язык пользователя для ошибки
                user_language = await db.get_user_language(supabase, user_id)
                error_message = get_text(user_language, 'command_admin_only')
                await update.message.reply_text(error_message)
                return
            return await func(update, context, *args, **kwargs)
        return wrapped

    @admin_only
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        welcome_message = get_text(user_language, 'admin_welcome')
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    @admin_only
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        try:
            # Получаем общую статистику
            user_count = await db.count_users(supabase)
            
            # Получаем дополнительную статистику
            all_users = await db.get_all_user_ids(supabase)
            
            total_credits = 0
            voice_enabled_count = 0
            negative_balance_count = 0
            
            for user_id_stat in all_users:
                user_data = await db.get_user_data(supabase, user_id_stat)
                if user_data:
                    credits = user_data.get('credits', 0)
                    total_credits += credits
                    
                    if credits < 0:
                        negative_balance_count += 1
                    
                    if user_data.get('voice_enabled', False):
                        voice_enabled_count += 1
            
            # Вычисляем средний баланс
            avg_credits = round(total_credits / user_count, 2) if user_count > 0 else 0
            voice_percentage = round(voice_enabled_count/user_count*100, 1) if user_count > 0 else 0
            
            if user_language == 'ru':
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
                    f"• Включили голосовые ответы: **{voice_enabled_count}** из {user_count} ({voice_percentage}%)"
                )
                
                if negative_balance_count > 0:
                    stats_message += f"\n\n⚠️ **Внимание:** {negative_balance_count} пользователей с отрицательным балансом!"
            elif user_language == 'pl':
                stats_message = (
                    f"📊 **Statystyki bota**\n\n"
                    f"👥 **Użytkownicy:**\n"
                    f"• Wszyscy użytkownicy: **{user_count}**\n"
                    f"• Z odpowiedziami głosowymi: **{voice_enabled_count}**\n"
                    f"• Z ujemnym saldem: **{negative_balance_count}**\n\n"
                    f"💰 **Kredyty:**\n"
                    f"• Łączne kredyty: **{total_credits}**\n"
                    f"• Średnie saldo: **{avg_credits}** kredytów\n\n"
                    f"🎙️ **Wiadomości głosowe:**\n"
                    f"• Włączyło odpowiedzi głosowe: **{voice_enabled_count}** z {user_count} ({voice_percentage}%)"
                )
                
                if negative_balance_count > 0:
                    stats_message += f"\n\n⚠️ **Uwaga:** {negative_balance_count} użytkowników z ujemnym saldem!"
            else:  # English
                stats_message = (
                    f"📊 **Bot Statistics**\n\n"
                    f"👥 **Users:**\n"
                    f"• Total users: **{user_count}**\n"
                    f"• With voice responses: **{voice_enabled_count}**\n"
                    f"• With negative balance: **{negative_balance_count}**\n\n"
                    f"💰 **Credits:**\n"
                    f"• Total credits: **{total_credits}**\n"
                    f"• Average balance: **{avg_credits}** credits\n\n"
                    f"🎙️ **Voice messages:**\n"
                    f"• Enabled voice responses: **{voice_enabled_count}** of {user_count} ({voice_percentage}%)"
                )
                
                if negative_balance_count > 0:
                    stats_message += f"\n\n⚠️ **Warning:** {negative_balance_count} users with negative balance!"
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            if user_language == 'ru':
                error_msg = f"❌ Ошибка при получении статистики: {e}"
            elif user_language == 'pl':
                error_msg = f"❌ Błąd podczas pobierania statystyk: {e}"
            else:
                error_msg = f"❌ Error getting statistics: {e}"
            await update.message.reply_text(error_msg)

    @admin_only
    async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        message_to_send = " ".join(context.args)
        if not message_to_send:
            error_message = get_text(user_language, 'admin_broadcast_no_message')
            await update.message.reply_text(error_message)
            return
            
        user_ids = await db.get_all_user_ids(supabase)
        start_message = get_text(user_language, 'admin_broadcast_start', count=len(user_ids))
        await update.message.reply_text(start_message)
        
        success_count, fail_count = 0, 0
        for target_user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=target_user_id, text=message_to_send)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                fail_count += 1
                print(f"Не удалось отправить сообщение {target_user_id}: {e}")
                
        complete_message = get_text(user_language, 'admin_broadcast_complete', success=success_count, failed=fail_count)
        await update.message.reply_text(complete_message)

    @admin_only
    async def add_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        try:
            if len(context.args) < 2:
                error_message = get_text(
                    user_language, 'admin_command_format_error',
                    command='/add_credits <user_id> <количество>' if user_language == 'ru' else '/add_credits <user_id> <ilość>' if user_language == 'pl' else '/add_credits <user_id> <amount>',
                    example='/add_credits 123456789 10'
                )
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
                
            target_user_id = int(context.args[0])
            amount = int(context.args[1])
            
            if amount <= 0:
                error_message = get_text(user_language, 'admin_credits_positive')
                await update.message.reply_text(error_message)
                return
            
            # Получаем текущий баланс пользователя
            current_balance = await db.get_user_credits(supabase, target_user_id)
            
            # Проверяем, существует ли пользователь
            user_data = await db.get_user_data(supabase, target_user_id)
            if not user_data:
                error_message = get_text(user_language, 'admin_user_not_found', user_id=target_user_id)
                await update.message.reply_text(error_message)
                return
            
            # Начисляем кредиты
            new_balance = await db.add_user_credits(supabase, target_user_id, amount)
            
            # Формируем сообщение админу
            admin_message = get_text(
                user_language, 'admin_credits_added_success',
                user_id=target_user_id, amount=amount,
                old_balance=current_balance, new_balance=new_balance
            )
            
            await update.message.reply_text(admin_message, parse_mode='Markdown')
            
            # Уведомляем пользователя о начислении кредитов на его языке
            try:
                target_user_language = await db.get_user_language(supabase, target_user_id)
                user_message = get_text(
                    target_user_language, 'admin_user_notified_credits_added',
                    amount=amount, balance=new_balance
                )
                
                await context.bot.send_message(chat_id=target_user_id, text=user_message, parse_mode='Markdown')
                
            except Exception as e:
                notification_failed = get_text(user_language, 'admin_notification_failed', error=e)
                await update.message.reply_text(notification_failed)
                
        except (IndexError, ValueError):
            error_message = get_text(
                user_language, 'admin_command_format_error',
                command='/add_credits <user_id> <количество>' if user_language == 'ru' else '/add_credits <user_id> <ilość>' if user_language == 'pl' else '/add_credits <user_id> <amount>',
                example='/add_credits 123456789 10'
            )
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception as e:
            if user_language == 'ru':
                error_msg = f"❌ Произошла ошибка: {e}"
            elif user_language == 'pl':
                error_msg = f"❌ Wystąpił błąd: {e}"
            else:
                error_msg = f"❌ An error occurred: {e}"
            await update.message.reply_text(error_msg)

    @admin_only
    async def remove_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        try:
            if len(context.args) < 2:
                if user_language == 'ru':
                    command_text = '/remove_credits <user_id> <количество>'
                    examples_text = "**Примеры:**\n• `/remove_credits 123456789 5` - снять 5 кредитов\n• `/remove_credits 123456789 10 force` - снять 10 кредитов (даже если уйдет в минус)"
                elif user_language == 'pl':
                    command_text = '/remove_credits <user_id> <ilość>'
                    examples_text = "**Przykłady:**\n• `/remove_credits 123456789 5` - usuń 5 kredytów\n• `/remove_credits 123456789 10 force` - usuń 10 kredytów (nawet jeśli spadnie poniżej zera)"
                else:
                    command_text = '/remove_credits <user_id> <amount>'
                    examples_text = "**Examples:**\n• `/remove_credits 123456789 5` - remove 5 credits\n• `/remove_credits 123456789 10 force` - remove 10 credits (even if goes negative)"
                
                error_message = get_text(
                    user_language, 'admin_command_format_error',
                    command=command_text, example=examples_text
                )
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
                
            target_user_id = int(context.args[0])
            amount = int(context.args[1])
            
            if amount <= 0:
                error_message = get_text(user_language, 'admin_credits_positive')
                await update.message.reply_text(error_message)
                return
            
            # Проверяем, есть ли флаг "force" для разрешения ухода в минус
            allow_negative = len(context.args) > 2 and context.args[2].lower() == "force"
            
            # Получаем текущий баланс пользователя
            current_balance = await db.get_user_credits(supabase, target_user_id)
            
            # Проверяем, существует ли пользователь
            user_data = await db.get_user_data(supabase, target_user_id)
            if not user_data:
                error_message = get_text(user_language, 'admin_user_not_found', user_id=target_user_id)
                await update.message.reply_text(error_message)
                return
            
            # Снимаем кредиты
            new_balance, success = await db.remove_user_credits(supabase, target_user_id, amount, allow_negative)
            
            if success:
                # Формируем сообщение админу
                admin_message = get_text(
                    user_language, 'admin_credits_removed_success',
                    user_id=target_user_id, amount=amount,
                    old_balance=current_balance, new_balance=new_balance
                )
                
                if new_balance < 0:
                    admin_message += f"\n\n{get_text(user_language, 'admin_balance_negative_warning')}"
                
                await update.message.reply_text(admin_message, parse_mode='Markdown')
                
                # Уведомляем пользователя о снятии кредитов на его языке
                try:
                    target_user_language = await db.get_user_language(supabase, target_user_id)
                    user_message = get_text(
                        target_user_language, 'admin_user_notified_credits_removed',
                        amount=amount, balance=new_balance
                    )
                    
                    if new_balance < 0:
                        user_message += f"\n\n{get_text(target_user_language, 'admin_user_balance_negative')}"
                    
                    await context.bot.send_message(chat_id=target_user_id, text=user_message, parse_mode='Markdown')
                    
                except Exception as e:
                    notification_failed = get_text(user_language, 'admin_notification_failed', error=e)
                    await update.message.reply_text(notification_failed)
            else:
                # Не удалось снять кредиты
                failed_message = get_text(
                    user_language, 'admin_credits_remove_failed',
                    user_id=target_user_id, current=current_balance, amount=amount,
                    command='/remove_credits'
                )
                await update.message.reply_text(failed_message, parse_mode='Markdown')
                
        except (IndexError, ValueError):
            if user_language == 'ru':
                command_text = '/remove_credits <user_id> <количество> [force]'
                examples_text = "**Примеры:**\n• `/remove_credits 123456789 5`\n• `/remove_credits 123456789 10 force`"
            elif user_language == 'pl':
                command_text = '/remove_credits <user_id> <ilość> [force]'
                examples_text = "**Przykłady:**\n• `/remove_credits 123456789 5`\n• `/remove_credits 123456789 10 force`"
            else:
                command_text = '/remove_credits <user_id> <amount> [force]'
                examples_text = "**Examples:**\n• `/remove_credits 123456789 5`\n• `/remove_credits 123456789 10 force`"
            
            error_message = get_text(
                user_language, 'admin_command_format_error',
                command=command_text, example=examples_text
            )
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception as e:
            if user_language == 'ru':
                error_msg = f"❌ Произошла ошибка: {e}"
            elif user_language == 'pl':
                error_msg = f"❌ Wystąpił błąd: {e}"
            else:
                error_msg = f"❌ An error occurred: {e}"
            await update.message.reply_text(error_msg)

    @admin_only
    async def user_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        try:
            if len(context.args) < 1:
                error_message = get_text(
                    user_language, 'admin_command_format_error',
                    command='/user_info <user_id>',
                    example='/user_info 123456789'
                )
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
                
            target_user_id = int(context.args[0])
            
            # Получаем данные пользователя
            user_data = await db.get_user_data(supabase, target_user_id)
            
            if not user_data:
                error_message = get_text(user_language, 'admin_user_not_found', user_id=target_user_id)
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
            
            # Получаем реферальную статистику
            referral_stats = await db.get_referral_stats(supabase, target_user_id)
            voice_stats = await db.get_voice_stats(supabase, target_user_id)
            
            # Формируем подробную информацию
            credits = user_data.get('credits', 0)
            mode = user_data.get('mode', 'Не установлен')
            model = user_data.get('model', 'Не установлен')
            state = user_data.get('state', 'chat')
            created_at = user_data.get('created_at', 'Неизвестно')
            interface_language = user_data.get('interface_language', 'en')
            
            # Голосовые настройки
            voice_enabled = user_data.get('voice_enabled', False)
            selected_voice = user_data.get('selected_voice', 'alloy')
            voice_language = user_data.get('voice_language', 'ru')
            
            # Реферальная информация
            referral_code = user_data.get('referral_code', 'Нет')
            invited_by = user_data.get('invited_by', 'Нет')
            invited_count = referral_stats.get('invited_count', 0)
            
            if user_language == 'ru':
                user_info_message = (
                    f"👤 **Информация о пользователе**\n\n"
                    f"**🆔 ID:** `{target_user_id}`\n"
                    f"**📅 Регистрация:** {created_at}\n"
                    f"**⚡ Состояние:** {state}\n"
                    f"**🌍 Язык интерфейса:** {interface_language.upper()}\n\n"
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
            elif user_language == 'pl':
                user_info_message = (
                    f"👤 **Informacje o użytkowniku**\n\n"
                    f"**🆔 ID:** `{target_user_id}`\n"
                    f"**📅 Rejestracja:** {created_at}\n"
                    f"**⚡ Stan:** {state}\n"
                    f"**🌍 Język interfejsu:** {interface_language.upper()}\n\n"
                    f"💰 **Saldo:** {credits} kredytów"
                )
                
                if credits < 0:
                    user_info_message += " ⚠️"
                
                user_info_message += (
                    f"\n\n🤖 **Ustawienia AI:**\n"
                    f"• Tryb: {mode}\n"
                    f"• Model: {model}\n\n"
                    f"🎙️ **Wiadomości głosowe:**\n"
                    f"• Włączone: {'Tak' if voice_enabled else 'Nie'}\n"
                    f"• Głos: {selected_voice}\n"
                    f"• Język: {voice_language.upper()}\n"
                    f"• Wysłane: {voice_stats['sent']}\n"
                    f"• Otrzymane: {voice_stats['received']}\n\n"
                    f"🔗 **Program referencyjny:**\n"
                    f"• Kod: `{referral_code}`\n"
                    f"• Zaproszony przez: {invited_by if invited_by != 'Нет' else 'Sam się zarejestrował'}\n"
                    f"• Zaproszeni znajomi: {invited_count}"
                )
            else:  # English
                user_info_message = (
                    f"👤 **User Information**\n\n"
                    f"**🆔 ID:** `{target_user_id}`\n"
                    f"**📅 Registration:** {created_at}\n"
                    f"**⚡ State:** {state}\n"
                    f"**🌍 Interface language:** {interface_language.upper()}\n\n"
                    f"💰 **Balance:** {credits} credits"
                )
                
                if credits < 0:
                    user_info_message += " ⚠️"
                
                user_info_message += (
                    f"\n\n🤖 **AI Settings:**\n"
                    f"• Mode: {mode}\n"
                    f"• Model: {model}\n\n"
                    f"🎙️ **Voice Messages:**\n"
                    f"• Enabled: {'Yes' if voice_enabled else 'No'}\n"
                    f"• Voice: {selected_voice}\n"
                    f"• Language: {voice_language.upper()}\n"
                    f"• Sent: {voice_stats['sent']}\n"
                    f"• Received: {voice_stats['received']}\n\n"
                    f"🔗 **Referral Program:**\n"
                    f"• Code: `{referral_code}`\n"
                    f"• Invited by: {invited_by if invited_by != 'Нет' else 'Self-registered'}\n"
                    f"• Friends invited: {invited_count}"
                )
            
            await update.message.reply_text(user_info_message, parse_mode='Markdown')
            
        except (IndexError, ValueError):
            error_message = get_text(
                user_language, 'admin_command_format_error',
                command='/user_info <user_id>',
                example='/user_info 123456789'
            )
            await update.message.reply_text(error_message, parse_mode='Markdown')
        except Exception as e:
            if user_language == 'ru':
                error_msg = f"❌ Произошла ошибка: {e}"
            elif user_language == 'pl':
                error_msg = f"❌ Wystąpił błąd: {e}"
            else:
                error_msg = f"❌ An error occurred: {e}"
            await update.message.reply_text(error_msg)

    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("add_credits", add_credits_command))
    application.add_handler(CommandHandler("remove_credits", remove_credits_command))
    application.add_handler(CommandHandler("user_info", user_info_command))