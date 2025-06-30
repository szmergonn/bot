# handlers/menu_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import CHAT_MODES, AVAILABLE_MODELS, AVAILABLE_VOICES, AVAILABLE_LANGUAGES, VOICE_TO_TEXT_COST, TEXT_TO_VOICE_COST, MESSAGE_COST
from database import db
from translations import get_text

# ИСПРАВЛЕНО: Принимаем клиент supabase
def register_handlers(application, supabase):

    async def build_main_menu(user_language):
        """Строит главное меню на нужном языке."""
        buttons = [
            [InlineKeyboardButton(get_text(user_language, 'chat_mode'), callback_data="submenu_modes")],
            [InlineKeyboardButton(get_text(user_language, 'select_model'), callback_data="submenu_models")],
            [InlineKeyboardButton(get_text(user_language, 'voice_messages'), callback_data="voice_settings")],
            [InlineKeyboardButton(get_text(user_language, 'streaming_enabled'), callback_data="streaming_settings")],
            [InlineKeyboardButton(get_text(user_language, 'generate_image'), callback_data="image_generate")],
            [InlineKeyboardButton(get_text(user_language, 'language_settings'), callback_data="language_settings")]
        ]
        return InlineKeyboardMarkup(buttons)

    async def build_modes_menu(user_language):
        """Строит меню режимов на нужном языке."""
        # Словарь для локализации режимов чата
        mode_translations = {
            'Помощник': {
                'ru': get_text('ru', 'chat_mode_assistant'),
                'en': get_text('en', 'chat_mode_assistant'), 
                'pl': get_text('pl', 'chat_mode_assistant')
            },
            'Шутник': {
                'ru': get_text('ru', 'chat_mode_joker'),
                'en': get_text('en', 'chat_mode_joker'),
                'pl': get_text('pl', 'chat_mode_joker')
            },
            'Переводчик': {
                'ru': get_text('ru', 'chat_mode_translator'),
                'en': get_text('en', 'chat_mode_translator'),
                'pl': get_text('pl', 'chat_mode_translator')
            }
        }
        
        mode_buttons = []
        for mode_key in CHAT_MODES.keys():
            # Получаем локализованное название
            localized_name = mode_translations.get(mode_key, {}).get(user_language, mode_key)
            mode_buttons.append([InlineKeyboardButton(localized_name, callback_data=f"mode_{mode_key}")])
        
        mode_buttons.append([InlineKeyboardButton(get_text(user_language, 'back'), callback_data="main_menu")])
        return InlineKeyboardMarkup(mode_buttons)

    async def build_model_menu(user_language):
        """Строит меню моделей на нужном языке."""
        buttons = [[InlineKeyboardButton(name, callback_data=f"model_{model_id}")] for name, model_id in AVAILABLE_MODELS.items()]
        buttons.append([InlineKeyboardButton(get_text(user_language, 'back'), callback_data="main_menu")])
        return InlineKeyboardMarkup(buttons)

    async def build_language_menu(user_language):
        """Строит меню выбора языка интерфейса."""
        buttons = [
            [InlineKeyboardButton(get_text(user_language, 'lang_russian'), callback_data="set_lang_ru")],
            [InlineKeyboardButton(get_text(user_language, 'lang_english'), callback_data="set_lang_en")],
            [InlineKeyboardButton(get_text(user_language, 'lang_polish'), callback_data="set_lang_pl")],
            [InlineKeyboardButton(get_text(user_language, 'back'), callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(buttons)
    
    async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_language = await db.get_user_language(supabase, chat_id)
        
        menu_text = get_text(user_language, 'main_menu')
        menu_markup = await build_main_menu(user_language)
        
        await update.message.reply_text(menu_text, reply_markup=menu_markup)

    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        user_id = query.from_user.id
        
        # Получаем язык пользователя для всех сообщений
        user_language = await db.get_user_language(supabase, user_id)
        
        if query.data == "main_menu":
            menu_text = get_text(user_language, 'main_menu')
            menu_markup = await build_main_menu(user_language)
            await query.edit_message_text(menu_text, reply_markup=menu_markup)
            
        elif query.data == "submenu_modes":
            mode_text = get_text(user_language, 'select_chat_mode')
            mode_markup = await build_modes_menu(user_language)
            await query.edit_message_text(mode_text, reply_markup=mode_markup)
            
        elif query.data == "submenu_models":
            model_text = get_text(user_language, 'select_model_menu')
            model_markup = await build_model_menu(user_language)
            await query.edit_message_text(model_text, reply_markup=model_markup)
            
        elif query.data == "language_settings":
            language_text = get_text(user_language, 'language_settings_title')
            language_text += "\n\n" + get_text(user_language, 'language_settings_hint')
            language_markup = await build_language_menu(user_language)
            await query.edit_message_text(language_text, reply_markup=language_markup, parse_mode='Markdown')
            
        elif query.data.startswith("set_lang_"):
            new_language = query.data.replace("set_lang_", "")
            # ОБНОВЛЕНО: Используем новую функцию с синхронизацией голосового языка
            success = await db.set_user_language_with_voice_sync(supabase, user_id, new_language)
            
            if success:
                # Получаем название языка на новом языке
                language_names = {
                    'ru': get_text(new_language, 'lang_russian'),
                    'en': get_text(new_language, 'lang_english'), 
                    'pl': get_text(new_language, 'lang_polish')
                }
                language_name = language_names.get(new_language, new_language)
                
                # ОБНОВЛЕНО: Уведомляем об изменении и голосового языка
                if new_language == 'ru':
                    success_text = f"✅ **Язык интерфейса изменен!**\n\nВыбранный язык: {language_name}\n\n🎙️ **Также изменен язык голосового общения** на русский\n\nТеперь бот будет общаться с вами на этом языке!"
                elif new_language == 'pl':
                    success_text = f"✅ **Język interfejsu zmieniony!**\n\nWybrany język: {language_name}\n\n🎙️ **Język komunikacji głosowej również zmieniony** na polski\n\nTeraz bot będzie komunikować się z tobą w tym języku!"
                else:  # English
                    success_text = f"✅ **Interface language changed!**\n\nSelected language: {language_name}\n\n🎙️ **Voice communication language also changed** to English\n\nNow the bot will communicate with you in this language!"
                
                main_menu_markup = await build_main_menu(new_language)
                await query.edit_message_text(success_text, reply_markup=main_menu_markup, parse_mode='Markdown')
            else:
                error_text = get_text(user_language, 'language_change_interface_error')
                main_menu_markup = await build_main_menu(user_language)
                await query.edit_message_text(error_text, reply_markup=main_menu_markup)
            
        elif query.data.startswith("mode_"):
            mode_name = query.data.split("_")[1]
            await db.set_user_mode(supabase, chat_id, mode_name)
            
            success_text = get_text(user_language, 'mode_changed', mode=mode_name)
            main_menu_markup = await build_main_menu(user_language)
            await query.edit_message_text(success_text, parse_mode='Markdown', reply_markup=main_menu_markup)
            
        elif query.data.startswith("model_"):
            model_id = query.data.split("model_")[1]
            await db.set_user_model(supabase, chat_id, model_id)
            model_name = next((name for name, mid in AVAILABLE_MODELS.items() if mid == model_id), model_id)
            
            success_text = get_text(user_language, 'model_changed', model=model_name)
            main_menu_markup = await build_main_menu(user_language)
            await query.edit_message_text(success_text, parse_mode='Markdown', reply_markup=main_menu_markup)
            
        elif query.data == "image_generate":
            await db.set_user_state(supabase, chat_id, "awaiting_image_prompt")
            prompt_text = get_text(user_language, 'image_prompt_request')
            await query.edit_message_text(text=prompt_text)
            
        # --- НОВЫЕ ОБРАБОТЧИКИ ДЛЯ ГОЛОСОВЫХ СООБЩЕНИЙ ---
        elif query.data == "voice_settings":
            await show_voice_settings(query, supabase, user_id, user_language)
            
        elif query.data == "voice_toggle":
            await toggle_voice_mode(query, supabase, user_id, user_language)
            
        elif query.data == "voice_select":
            await show_voice_selection(query, user_language)
            
        elif query.data == "voice_language":
            await show_language_selection(query, user_language)
            
        elif query.data.startswith("voice_set_"):
            voice_id = query.data.replace("voice_set_", "")
            await set_user_voice(query, supabase, user_id, voice_id, user_language)
            
        elif query.data.startswith("voice_lang_"):
            language_code = query.data.replace("voice_lang_", "")
            await set_user_voice_language(query, supabase, user_id, language_code, user_language)
            
        elif query.data == "voice_settings_back":
            await show_voice_settings(query, supabase, user_id, user_language)
            
        # --- НОВЫЕ ОБРАБОТЧИКИ ДЛЯ STREAMING RESPONSE ---
        elif query.data == "streaming_settings":
            await show_streaming_settings(query, supabase, user_id, user_language)
            
        elif query.data == "streaming_toggle":
            await toggle_streaming_mode(query, supabase, user_id, user_language)
            
        elif query.data == "streaming_settings_back":
            await show_streaming_settings(query, supabase, user_id, user_language)

    # --- ФУНКЦИИ ДЛЯ РАБОТЫ С ГОЛОСОВЫМИ НАСТРОЙКАМИ ---

    async def show_voice_settings(query, supabase, user_id, user_language):
        """Показывает настройки голосовых сообщений."""
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
        
        total_voice_cost = VOICE_TO_TEXT_COST + TEXT_TO_VOICE_COST + MESSAGE_COST
        
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
            f"{get_text(user_language, 'voice_response_cost', cost=total_voice_cost)}\n\n"
            f"{get_text(user_language, 'voice_credit_warning', cost=total_voice_cost)}\n\n"
            f"{get_text(user_language, 'voice_test_hint')}"
        )
        
        toggle_text = get_text(user_language, 'voice_toggle_enable') if not voice_settings.get('voice_enabled') else get_text(user_language, 'voice_toggle_disable')
        
        keyboard = [
            [InlineKeyboardButton(toggle_text, callback_data="voice_toggle")],
            [InlineKeyboardButton(get_text(user_language, 'change_voice'), callback_data="voice_select")],
            [InlineKeyboardButton(get_text(user_language, 'voice_recognition_lang'), callback_data="voice_language")],
            [InlineKeyboardButton(get_text(user_language, 'back_to_menu'), callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def toggle_voice_mode(query, supabase, user_id, user_language):
        """Переключает режим голосовых ответов."""
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        new_status = not voice_settings.get('voice_enabled', False)
        
        success = await db.set_voice_enabled(supabase, user_id, new_status)
        
        if success:
            if new_status:
                message_text = get_text(user_language, 'voice_enabled_success')
            else:
                message_text = get_text(user_language, 'voice_disabled_success')
                
            await query.edit_message_text(
                message_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")
                ]])
            )
        else:
            error_text = get_text(user_language, 'voice_change_error')
            await query.edit_message_text(
                error_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")
                ]])
            )

    async def show_voice_selection(query, user_language):
        """Показывает меню выбора голоса."""
        buttons = []
        for voice_name, voice_id in AVAILABLE_VOICES.items():
            buttons.append([InlineKeyboardButton(
                voice_name, 
                callback_data=f"voice_set_{voice_id}"
            )])
        
        buttons.append([InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")])
        
        voice_descriptions = {
            'ru': "🎭 **Выберите голос для ответов:**\n\n🎭 **Alloy** - Нейтральный голос\n🔊 **Echo** - Мужской голос\n📖 **Fable** - Британский акцент\n💎 **Onyx** - Глубокий мужской\n✨ **Nova** - Женский голос\n🌟 **Shimmer** - Мягкий женский\n\nВыберите понравившийся:",
            'en': "🎭 **Choose voice for responses:**\n\n🎭 **Alloy** - Neutral voice\n🔊 **Echo** - Male voice\n📖 **Fable** - British accent\n💎 **Onyx** - Deep male\n✨ **Nova** - Female voice\n🌟 **Shimmer** - Soft female\n\nChoose your favorite:",
            'pl': "🎭 **Wybierz głos do odpowiedzi:**\n\n🎭 **Alloy** - Neutralny głos\n🔊 **Echo** - Męski głos\n📖 **Fable** - Brytyjski akcent\n💎 **Onyx** - Głęboki męski\n✨ **Nova** - Kobiecy głos\n🌟 **Shimmer** - Miękki kobiecy\n\nWybierz swój ulubiony:"
        }
        
        description = voice_descriptions.get(user_language, voice_descriptions['en'])
        
        await query.edit_message_text(
            description,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def set_user_voice(query, supabase, user_id, voice_id, user_language):
        """Устанавливает выбранный голос."""
        success = await db.set_user_voice(supabase, user_id, voice_id)
        
        if success:
            voice_name = next((name for name, vid in AVAILABLE_VOICES.items() if vid == voice_id), voice_id)
            success_text = get_text(user_language, 'voice_changed_success', voice=voice_name)
            await query.edit_message_text(
                success_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")
                ]])
            )
        else:
            error_text = get_text(user_language, 'voice_change_error_voice')
            await query.edit_message_text(
                error_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")
                ]])
            )

    async def show_language_selection(query, user_language):
        """Показывает меню выбора языка распознавания (только 3 языка)."""
        buttons = []
        for language_name, language_code in AVAILABLE_LANGUAGES.items():
            buttons.append([InlineKeyboardButton(
                language_name, 
                callback_data=f"voice_lang_{language_code}"
            )])
        
        buttons.append([InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")])
        
        language_descriptions = {
            'ru': "🌍 **Выберите язык для распознавания речи:**\n\nВыберите язык, на котором вы будете говорить в голосовых сообщениях.\nЭто поможет боту точнее распознавать вашу речь:",
            'en': "🌍 **Choose language for speech recognition:**\n\nSelect the language you will speak in voice messages.\nThis will help the bot recognize your speech more accurately:",
            'pl': "🌍 **Wybierz język rozpoznawania mowy:**\n\nWybierz język, którym będziesz mówić w wiadomościach głosowych.\nTo pomoże botowi dokładniej rozpoznawać twoją mowę:"
        }
        
        description = language_descriptions.get(user_language, language_descriptions['en'])
        
        await query.edit_message_text(
            description,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def set_user_voice_language(query, supabase, user_id, language_code, user_language):
        """Устанавливает выбранный язык распознавания."""
        success = await db.set_user_voice_language(supabase, user_id, language_code)
        
        if success:
            language_name = next((name for name, code in AVAILABLE_LANGUAGES.items() if code == language_code), language_code)
            success_text = get_text(user_language, 'language_changed_success', language=language_name)
            await query.edit_message_text(
                success_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")
                ]])
            )
        else:
            error_text = get_text(user_language, 'language_change_error')
            await query.edit_message_text(
                error_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="voice_settings_back")
                ]])
            )

    # --- ФУНКЦИИ ДЛЯ РАБОТЫ С STREAMING НАСТРОЙКАМИ ---

    async def show_streaming_settings(query, supabase, user_id, user_language):
        """Показывает настройки потоковых ответов."""
        streaming_enabled = await db.get_user_streaming_setting(supabase, user_id)
        
        status = get_text(user_language, 'streaming_enabled_status') if streaming_enabled else get_text(user_language, 'streaming_disabled_status')
        
        settings_text = (
            f"{get_text(user_language, 'streaming_settings_title')}\n\n"
            f"{get_text(user_language, 'streaming_status', status=status)}\n\n"
            f"{get_text(user_language, 'streaming_description')}"
        )
        
        toggle_text = get_text(user_language, 'streaming_toggle_enable') if not streaming_enabled else get_text(user_language, 'streaming_toggle_disable')
        
        keyboard = [
            [InlineKeyboardButton(toggle_text, callback_data="streaming_toggle")],
            [InlineKeyboardButton(get_text(user_language, 'back_to_menu'), callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def toggle_streaming_mode(query, supabase, user_id, user_language):
        """Переключает режим потоковых ответов."""
        current_setting = await db.get_user_streaming_setting(supabase, user_id)
        new_status = not current_setting
        
        success = await db.set_user_streaming(supabase, user_id, new_status)
        
        if success:
            if new_status:
                message_text = get_text(user_language, 'streaming_enabled_success')
            else:
                message_text = get_text(user_language, 'streaming_disabled_success')
                
            await query.edit_message_text(
                message_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="streaming_settings_back")
                ]])
            )
        else:
            error_text = get_text(user_language, 'streaming_change_error')
            await query.edit_message_text(
                error_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 " + get_text(user_language, 'back'), callback_data="streaming_settings_back")
                ]])
            )

    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))