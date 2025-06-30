# handlers/voice_handler.py

import os
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from openai import OpenAI
from database import db
from config import (
    VOICE_TO_TEXT_COST, TEXT_TO_VOICE_COST, MAX_VOICE_DURATION,
    AVAILABLE_VOICES, MESSAGE_COST
)

def register_handlers(application, openai_client: OpenAI, supabase):
    
    async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает голосовые сообщения - распознавание речи."""
        user_id = update.effective_user.id
        
        # Проверяем баланс
        current_credits = await db.get_user_credits(supabase, user_id)
        if current_credits < VOICE_TO_TEXT_COST:
            await update.message.reply_text(
                f"❌ Недостаточно кредитов для распознавания речи.\n"
                f"Нужно: {VOICE_TO_TEXT_COST} кредитов, у вас: {current_credits}"
            )
            return
        
        voice = update.message.voice
        
        # Проверяем длительность
        if voice.duration > MAX_VOICE_DURATION:
            await update.message.reply_text(
                f"❌ Голосовое сообщение слишком длинное!\n"
                f"Максимум: {MAX_VOICE_DURATION} секунд, у вас: {voice.duration} секунд"
            )
            return
        
        # Получаем настройки пользователя
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        language = voice_settings.get('voice_language', 'ru')
        
        await update.message.reply_text("🎙️ Распознаю речь...")
        
        try:
            # Скачиваем голосовое сообщение
            voice_file = await context.bot.get_file(voice.file_id)
            voice_bytes = io.BytesIO()
            await voice_file.download_to_memory(voice_bytes)
            voice_bytes.seek(0)
            voice_bytes.name = "voice.ogg"  # OpenAI требует имя файла
            
            # Распознаем речь через OpenAI Whisper
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=voice_bytes,
                language=language,
                response_format="text"
            )
            
            # Списываем кредиты
            await db.deduct_user_credits(supabase, user_id, VOICE_TO_TEXT_COST)
            
            # Обновляем статистику
            await db.increment_voice_stats(supabase, user_id, "received")
            
            # Отправляем результат распознавания
            await update.message.reply_text(
                f"🎙️ **Распознанный текст:**\n{transcript}\n\n"
                f"💰 Списано {VOICE_TO_TEXT_COST} кредитов",
                parse_mode='Markdown'
            )
            
            # Проверяем, нужно ли отвечать голосом
            if voice_settings.get('voice_enabled', False):
                await generate_voice_response(update, context, openai_client, supabase, transcript)
            else:
                # Обычный текстовый ответ через AI
                await process_text_for_ai(update, context, openai_client, supabase, transcript)
                
        except Exception as e:
            print(f"Ошибка при распознавании речи: {e}")
            await update.message.reply_text(
                "❌ Не удалось распознать речь. Попробуйте еще раз.\n"
                "Кредиты не были списаны."
            )

    async def generate_voice_response(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    openai_client: OpenAI, supabase, text: str):
        """Генерирует голосовой ответ на текст."""
        user_id = update.effective_user.id
        
        # Проверяем баланс для голосового ответа
        current_credits = await db.get_user_credits(supabase, user_id)
        if current_credits < TEXT_TO_VOICE_COST + MESSAGE_COST:
            await update.message.reply_text(
                f"❌ Недостаточно кредитов для голосового ответа.\n"
                f"Нужно: {TEXT_TO_VOICE_COST + MESSAGE_COST} кредитов, у вас: {current_credits}"
            )
            return
        
        try:
            # Получаем текстовый ответ от AI
            user_data = await db.get_user_data(supabase, user_id)
            from config import CHAT_MODES
            system_prompt = CHAT_MODES.get(user_data['mode'], "Ты — полезный ассистент.")
            history = await db.get_user_history(supabase, user_id)
            
            messages_for_api = [
                {"role": "system", "content": system_prompt}
            ] + history + [
                {"role": "user", "content": text}
            ]
            
            # Получаем ответ от AI
            response = openai_client.chat.completions.create(
                model=user_data['model'],
                messages=messages_for_api,
                max_tokens=500  # Ограничиваем для голосового ответа
            )
            
            ai_response = response.choices[0].message.content
            
            # Генерируем голосовой ответ
            voice_settings = await db.get_user_voice_settings(supabase, user_id)
            selected_voice = voice_settings.get('selected_voice', 'alloy')
            
            await update.message.reply_text("🔊 Генерирую голосовой ответ...")
            
            # Создаем TTS через OpenAI
            tts_response = openai_client.audio.speech.create(
                model="tts-1",
                voice=selected_voice,
                input=ai_response,
                response_format="mp3"
            )
            
            # Конвертируем в BytesIO для отправки
            audio_data = io.BytesIO(tts_response.content)
            audio_data.name = "voice_response.mp3"
            audio_data.seek(0)
            
            # Списываем кредиты
            await db.deduct_user_credits(supabase, user_id, TEXT_TO_VOICE_COST + MESSAGE_COST)
            
            # Сохраняем в историю
            await db.add_message_to_history(supabase, user_id, "user", text)
            await db.add_message_to_history(supabase, user_id, "assistant", ai_response)
            
            # Обновляем статистику
            await db.increment_voice_stats(supabase, user_id, "sent")
            
            # Отправляем голосовое сообщение
            await update.message.reply_voice(
                voice=audio_data,
                caption=f"🔊 Голосовой ответ\n💰 Списано {TEXT_TO_VOICE_COST + MESSAGE_COST} кредитов"
            )
            
        except Exception as e:
            print(f"Ошибка при генерации голосового ответа: {e}")
            await update.message.reply_text(
                "❌ Не удалось сгенерировать голосовой ответ.\n"
                "Попробуйте текстовый режим."
            )

    async def process_text_for_ai(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                openai_client: OpenAI, supabase, text: str):
        """Обрабатывает текст через AI (обычный текстовый ответ)."""
        # Импортируем функцию из message_handlers
        from handlers.message_handlers import chat_with_ai
        
        # Создаем фейковый update с текстом
        class FakeMessage:
            def __init__(self, text):
                self.text = text
        
        fake_update = type('obj', (object,), {
            'effective_chat': type('obj', (object,), {'id': update.effective_chat.id})(),
            'message': FakeMessage(text)
        })()
        
        await chat_with_ai(fake_update, context, openai_client, supabase)

    # --- КОМАНДЫ ДЛЯ НАСТРОЙКИ ГОЛОСА ---

    async def voice_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню настроек голоса (доступно через /voice)."""
        user_id = update.effective_user.id
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        voice_stats = await db.get_voice_stats(supabase, user_id)
        
        # Найдем название выбранного голоса
        current_voice_name = "Не найден"
        for name, voice_id in AVAILABLE_VOICES.items():
            if voice_id == voice_settings.get('selected_voice'):
                current_voice_name = name
                break
        
        status = "🔊 Включены" if voice_settings.get('voice_enabled') else "🔇 Выключены"
        
        settings_text = (
            f"🎙️ **Настройки голосовых сообщений**\n\n"
            f"**Статус:** {status}\n"
            f"**Текущий голос:** {current_voice_name}\n"
            f"**Язык распознавания:** {voice_settings.get('voice_language', 'ru').upper()}\n\n"
            f"📊 **Статистика:**\n"
            f"• Отправлено голосовых: {voice_stats['sent']}\n"
            f"• Получено голосовых: {voice_stats['received']}\n\n"
            f"💰 **Стоимость:**\n"
            f"• Распознавание речи: {VOICE_TO_TEXT_COST} кредитов\n"
            f"• Голосовой ответ: {TEXT_TO_VOICE_COST} кредитов\n\n"
            f"ℹ️ Для настройки используйте /menu → 🎙️ Голосовые сообщения"
        )
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')

    # Регистрируем только обработчики голосовых сообщений и команду
    application.add_handler(MessageHandler(filters.VOICE, voice_message_handler))
    application.add_handler(CommandHandler("voice", voice_settings_command))