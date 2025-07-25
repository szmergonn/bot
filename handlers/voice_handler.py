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
from translations import get_text

def register_handlers(application, openai_client: OpenAI, supabase):
    
    async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает голосовые сообщения - распознавание речи."""
        user_id = update.effective_user.id
        print(f"🎙️ ПОЛУЧЕНО ГОЛОСОВОЕ СООБЩЕНИЕ от пользователя {user_id}")
        
        # Получаем язык пользователя
        user_language = await db.get_user_language(supabase, user_id)
        
        # НОВОЕ: Синхронизируем голосовой язык с интерфейсом при первом использовании
        await db.sync_voice_language_with_interface(supabase, user_id)
        
        # Получаем настройки пользователя для определения нужного количества кредитов
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        voice_enabled = voice_settings.get('voice_enabled', False)
        
        # Определяем нужное количество кредитов
        if voice_enabled:
            # Если включены голосовые ответы: распознавание + генерация голоса + сообщение AI
            required_credits = VOICE_TO_TEXT_COST + TEXT_TO_VOICE_COST + MESSAGE_COST
            operation_description = get_text(user_language, 'voice_response_cost', cost=required_credits).replace('• ', '').replace(' кредитов (распознавание + синтез + AI)', '').replace(' credits (recognition + synthesis + AI)', '').replace(' kredytów (rozpoznawanie + synteza + AI)', '')
        else:
            # Если голосовые ответы выключены: только распознавание
            required_credits = VOICE_TO_TEXT_COST
            operation_description = get_text(user_language, 'voice_recognition_cost', cost=required_credits).replace('• ', '').replace(' кредитов', '').replace(' credits', '').replace(' kredytów', '')
        
        # Проверяем баланс
        current_credits = await db.get_user_credits(supabase, user_id)
        print(f"💰 Баланс пользователя: {current_credits} кредитов (нужно: {required_credits})")
        
        if current_credits < required_credits:
            if voice_enabled and current_credits >= VOICE_TO_TEXT_COST:
                # Достаточно для распознавания, но не для голосового ответа
                error_message = get_text(
                    user_language, 'insufficient_credits_voice_full',
                    current=current_credits,
                    needed=required_credits,
                    recognition_cost=VOICE_TO_TEXT_COST
                )
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
            else:
                # Недостаточно даже для распознавания
                error_message = get_text(
                    user_language, 'insufficient_credits_voice_recognition',
                    operation=operation_description,
                    current=current_credits,
                    needed=required_credits
                )
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
        
        voice = update.message.voice
        print(f"🎵 Длительность голосового: {voice.duration} секунд")
        
        # Проверяем длительность
        if voice.duration > MAX_VOICE_DURATION:
            print(f"❌ Голосовое слишком длинное: {voice.duration} > {MAX_VOICE_DURATION}")
            error_message = get_text(
                user_language, 'voice_too_long',
                max_duration=MAX_VOICE_DURATION,
                duration=voice.duration
            )
            await update.message.reply_text(error_message)
            return
        
        # ОБНОВЛЕНО: Используем язык голосового общения (синхронизированный с интерфейсом)
        language = voice_settings.get('voice_language', user_language)
        print(f"🌍 Язык распознавания: {language} (интерфейс: {user_language})")
        
        processing_message = get_text(user_language, 'recognizing_speech')
        await update.message.reply_text(processing_message)
        
        try:
            print("📥 Скачиваю голосовое сообщение...")
            # Скачиваем голосовое сообщение
            voice_file = await context.bot.get_file(voice.file_id)
            voice_bytes = io.BytesIO()
            await voice_file.download_to_memory(voice_bytes)
            voice_bytes.seek(0)
            voice_bytes.name = "voice.ogg"  # OpenAI требует имя файла
            
            print("🤖 Отправляю в OpenAI Whisper...")
            # Распознаем речь через OpenAI Whisper
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=voice_bytes,
                language=language,
                response_format="text"
            )
            
            print(f"✅ Распознано: {transcript}")
            
            # Списываем кредиты за распознавание
            await db.deduct_user_credits(supabase, user_id, VOICE_TO_TEXT_COST)
            
            # Обновляем статистику
            await db.increment_voice_stats(supabase, user_id, "received")
            
            # Отправляем результат распознавания
            recognition_message = get_text(
                user_language, 'recognized_text',
                text=transcript,
                cost=VOICE_TO_TEXT_COST
            )
            await update.message.reply_text(recognition_message, parse_mode='Markdown')
            
            # Проверяем, нужно ли отвечать голосом
            if voice_enabled:
                print("🔊 Генерирую голосовой ответ...")
                await generate_voice_response(update, context, openai_client, supabase, transcript, user_language)
            else:
                print("💬 Генерирую текстовый ответ...")
                # Обычный текстовый ответ через AI
                await process_text_for_ai(update, context, openai_client, supabase, transcript, user_language)
                
        except Exception as e:
            print(f"❌ ОШИБКА при распознавании речи: {e}")
            import traceback
            traceback.print_exc()
            error_message = get_text(user_language, 'voice_recognition_error')
            await update.message.reply_text(error_message)

    async def generate_voice_response(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    openai_client: OpenAI, supabase, text: str, user_language: str):
        """Генерирует голосовой ответ на текст."""
        user_id = update.effective_user.id
        
        try:
            # Получаем текстовый ответ от AI
            user_data = await db.get_user_data(supabase, user_id)
            
            # ОБНОВЛЕНО: Используем многоязычный системный промпт
            from config import get_system_prompt
            system_prompt = get_system_prompt(user_data['mode'], user_language)
            history = await db.get_user_history(supabase, user_id)
            
            messages_for_api = [
                {"role": "system", "content": system_prompt}
            ] + history + [
                {"role": "user", "content": text}
            ]
            
            print(f"🤖 Используем системный промпт на языке {user_language}: {system_prompt[:50]}...")
            
            # Получаем ответ от AI
            response = openai_client.chat.completions.create(
                model=user_data['model'],
                messages=messages_for_api,
                max_tokens=500  # Ограничиваем для голосового ответа
            )
            
            ai_response = response.choices[0].message.content
            print(f"🤖 AI ответ: {ai_response[:50]}...")
            
            # Генерируем голосовой ответ
            voice_settings = await db.get_user_voice_settings(supabase, user_id)
            selected_voice = voice_settings.get('selected_voice', 'alloy')
            
            generating_message = get_text(user_language, 'generating_voice_response')
            await update.message.reply_text(generating_message)
            
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
            
            # Списываем кредиты за TTS и AI ответ
            total_cost = TEXT_TO_VOICE_COST + MESSAGE_COST
            await db.deduct_user_credits(supabase, user_id, total_cost)
            
            # Сохраняем в историю
            await db.add_message_to_history(supabase, user_id, "user", text)
            await db.add_message_to_history(supabase, user_id, "assistant", ai_response)
            
            # Обновляем статистику
            await db.increment_voice_stats(supabase, user_id, "sent")
            
            # Отправляем голосовое сообщение
            caption = get_text(user_language, 'voice_response_caption', cost=total_cost)
            await update.message.reply_voice(
                voice=audio_data,
                caption=caption
            )
            
        except Exception as e:
            print(f"Ошибка при генерации голосового ответа: {e}")
            error_message = get_text(user_language, 'voice_generation_error')
            await update.message.reply_text(error_message)

    async def process_text_for_ai(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                openai_client: OpenAI, supabase, text: str, user_language: str):
        """Обрабатывает текст через AI (текстовый ответ на голосовое сообщение)."""
        user_id = update.effective_user.id
        
        try:
            # Получаем настройки пользователя
            user_data = await db.get_user_data(supabase, user_id)
            current_credits = await db.get_user_credits(supabase, user_id)
            
            # Проверяем баланс для текстового ответа
            if current_credits < MESSAGE_COST:
                error_message = get_text(
                    user_language, 'insufficient_credits_voice_recognition',
                    operation=get_text(user_language, 'insufficient_credits_chat', cost=MESSAGE_COST).replace(f"Для ответа нужно: {MESSAGE_COST}.", "ответа AI").replace(f"Need for response: {MESSAGE_COST}.", "AI response").replace(f"Potrzebujesz na odpowiedź: {MESSAGE_COST}.", "odpowiedzi AI"),
                    current=current_credits,
                    needed=MESSAGE_COST
                )
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
            
            # ОБНОВЛЕНО: Используем многоязычный системный промпт
            from config import get_system_prompt
            current_mode_name = user_data['mode']
            current_model = user_data['model']
            streaming_enabled = user_data.get('streaming_enabled', True)
            history = await db.get_user_history(supabase, user_id)
            system_prompt = get_system_prompt(current_mode_name, user_language)
            
            print(f"🤖 Используем системный промпт на языке {user_language}: {system_prompt[:50]}...")
            
            # Формируем сообщения для API
            messages_for_api = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": text}]

            # НОВОЕ: Проверяем, включены ли потоковые ответы
            if streaming_enabled:
                await process_text_streaming(update, context, openai_client, supabase, messages_for_api, current_model, user_language, text, user_id)
            else:
                await process_text_regular(update, context, openai_client, supabase, messages_for_api, current_model, user_language, text, user_id)
                
        except Exception as e:
            print(f"❌ ОШИБКА при генерации текстового ответа: {e}")
            import traceback
            traceback.print_exc()
            error_message = get_text(user_language, 'text_response_error')
            await update.message.reply_text(error_message)

    async def process_text_streaming(update: Update, context: ContextTypes.DEFAULT_TYPE, openai_client: OpenAI, supabase, messages_for_api, model, user_language, original_text, user_id):
        """Обрабатывает текстовый ответ в потоковом режиме."""
        try:
            # Инициализируем потоковый ответ
            from streaming import StreamingResponse, stream_openai_response
            streaming_handler = StreamingResponse(update, context, user_language)
            
            # Запускаем потоковый ответ
            success = await streaming_handler.start_streaming()
            if not success:
                # Fallback на обычный режим
                await process_text_regular(update, context, openai_client, supabase, messages_for_api, model, user_language, original_text, user_id)
                return
            
            # Получаем потоковый ответ от OpenAI
            ai_response_text = await stream_openai_response(openai_client, messages_for_api, model, streaming_handler)
            
            # Завершаем потоковый ответ
            await streaming_handler.finalize_message(
                final_text=ai_response_text,
                add_credits_info=True,
                credits_cost=MESSAGE_COST
            )
            
            # Списываем кредиты и сохраняем в историю
            await db.deduct_user_credits(supabase, user_id, MESSAGE_COST)
            await db.add_message_to_history(supabase, user_id, "user", original_text)
            await db.add_message_to_history(supabase, user_id, "assistant", ai_response_text)
            
        except Exception as e:
            print(f"❌ Ошибка в потоковом режиме (голосовой): {e}")
            # Fallback на обычный режим
            await process_text_regular(update, context, openai_client, supabase, messages_for_api, model, user_language, original_text, user_id)

    async def process_text_regular(update: Update, context: ContextTypes.DEFAULT_TYPE, openai_client: OpenAI, supabase, messages_for_api, model, user_language, original_text, user_id):
        """Обрабатывает текстовый ответ в обычном режиме."""
        await context.bot.send_chat_action(chat_id=user_id, action='typing')
        
        # Получаем ответ от AI
        response = openai_client.chat.completions.create(
            model=model, 
            messages=messages_for_api
        )
        ai_response_text = response.choices[0].message.content
        
        print(f"🤖 AI ответ: {ai_response_text[:50]}...")
        
        # Списываем кредиты и сохраняем в историю
        await db.deduct_user_credits(supabase, user_id, MESSAGE_COST)
        await db.add_message_to_history(supabase, user_id, "user", original_text)
        await db.add_message_to_history(supabase, user_id, "assistant", ai_response_text)
        
        # Отправляем ответ
        response_message = f"{ai_response_text}\n\n💰 {get_text(user_language, 'recognized_text', text='', cost=MESSAGE_COST).split('💰')[1].strip()}"
        await update.message.reply_text(response_message)

    # --- КОМАНДЫ ДЛЯ НАСТРОЙКИ ГОЛОСА ---

    async def voice_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню настроек голоса (доступно через /voice)."""
        user_id = update.effective_user.id
        user_language = await db.get_user_language(supabase, user_id)
        
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        voice_stats = await db.get_voice_stats(supabase, user_id)
        
        # Найдем название выбранного голоса
        current_voice_name = "Не найден"
        for name, voice_id in AVAILABLE_VOICES.items():
            if voice_id == voice_settings.get('selected_voice'):
                current_voice_name = name
                break
        
        # Найдем название выбранного языка (только из 3 доступных)
        current_language_name = "Не найден"
        current_lang_code = voice_settings.get('voice_language', 'ru')
        for name, lang_code in AVAILABLE_LANGUAGES.items():
            if lang_code == current_lang_code:
                current_language_name = name
                break
        
        status = get_text(user_language, 'voice_enabled') if voice_settings.get('voice_enabled') else get_text(user_language, 'voice_disabled')
        
        settings_text = (
            f"{get_text(user_language, 'voice_settings_title')}\n\n"
            f"{get_text(user_language, 'voice_status', status=status)}\n"
            f"{get_text(user_language, 'current_voice', voice=current_voice_name)}\n"
            f"{get_text(user_language, 'recognition_language', language=current_language_name)}\n\n"
            f"{get_text(user_language, 'voice_statistics')}\n"
            f"{get_text(user_language, 'voice_sent', count=voice_stats['sent'])}\n"
            f"{get_text(user_language, 'voice_received', count=voice_stats['received'])}\n\n"
            f"{get_text(user_language, 'voice_costs')}\n"
            f"{get_text(user_language, 'voice_recognition_cost', cost=VOICE_TO_TEXT_COST)}\n"
            f"{get_text(user_language, 'voice_response_cost', cost=TEXT_TO_VOICE_COST)}\n\n"
            f"ℹ️ {get_text(user_language, 'voice_test_hint').replace('ℹ️ ', '')}"
        )
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')

    # Регистрируем только обработчики голосовых сообщений и команду
    application.add_handler(MessageHandler(filters.VOICE, voice_message_handler))
    application.add_handler(CommandHandler("voice", voice_settings_command))