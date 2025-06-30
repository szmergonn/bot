# handlers/menu_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import CHAT_MODES, AVAILABLE_MODELS, AVAILABLE_VOICES, AVAILABLE_LANGUAGES, VOICE_TO_TEXT_COST, TEXT_TO_VOICE_COST
from database import db

# ИСПРАВЛЕНО: Принимаем клиент supabase
def register_handlers(application, supabase):

    def build_main_menu():
        buttons = [
            [InlineKeyboardButton("🗣️ Режим общения", callback_data="submenu_modes")],
            [InlineKeyboardButton("🧠 Выбрать модель", callback_data="submenu_models")],
            [InlineKeyboardButton("🎙️ Голосовые сообщения", callback_data="voice_settings")],
            [InlineKeyboardButton("🖼️ Сгенерировать изображение", callback_data="image_generate")]
        ]
        return InlineKeyboardMarkup(buttons)

    def build_modes_menu():
        mode_buttons = [[InlineKeyboardButton(mode, callback_data=f"mode_{mode}")] for mode in CHAT_MODES.keys()]
        mode_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        return InlineKeyboardMarkup(mode_buttons)

    def build_model_menu():
        buttons = [[InlineKeyboardButton(name, callback_data=f"model_{model_id}")] for name, model_id in AVAILABLE_MODELS.items()]
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
        return InlineKeyboardMarkup(buttons)
    
    async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Главное меню:", reply_markup=build_main_menu())

    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        user_id = query.from_user.id
        
        if query.data == "main_menu":
            await query.edit_message_text("Главное меню:", reply_markup=build_main_menu())
            
        elif query.data == "submenu_modes":
            await query.edit_message_text("Выберите режим общения:", reply_markup=build_modes_menu())
            
        elif query.data == "submenu_models":
            await query.edit_message_text("Выберите модель для общения:", reply_markup=build_model_menu())
            
        elif query.data.startswith("mode_"):
            mode_name = query.data.split("_")[1]
            await db.set_user_mode(supabase, chat_id, mode_name)
            await query.edit_message_text(f"Режим изменен на: *{mode_name}*. Возвращаю в главное меню...", parse_mode='Markdown', reply_markup=build_main_menu())
            
        elif query.data.startswith("model_"):
            model_id = query.data.split("model_")[1]
            await db.set_user_model(supabase, chat_id, model_id)
            model_name = next((name for name, mid in AVAILABLE_MODELS.items() if mid == model_id), model_id)
            await query.edit_message_text(f"Модель изменена на: *{model_name}*. Возвращаю в главное меню...", parse_mode='Markdown', reply_markup=build_main_menu())
            
        elif query.data == "image_generate":
            await db.set_user_state(supabase, chat_id, "awaiting_image_prompt")
            await query.edit_message_text(text="Отлично! Присылайте текстовый запрос для создания картинки.")
            
        # --- НОВЫЕ ОБРАБОТЧИКИ ДЛЯ ГОЛОСОВЫХ СООБЩЕНИЙ ---
        elif query.data == "voice_settings":
            await show_voice_settings(query, supabase, user_id)
            
        elif query.data == "voice_toggle":
            await toggle_voice_mode(query, supabase, user_id)
            
        elif query.data == "voice_select":
            await show_voice_selection(query)
            
        elif query.data == "voice_language":
            await show_language_selection(query)
            
        elif query.data.startswith("voice_set_"):
            voice_id = query.data.replace("voice_set_", "")
            await set_user_voice(query, supabase, user_id, voice_id)
            
        elif query.data.startswith("voice_lang_"):
            language_code = query.data.replace("voice_lang_", "")
            await set_user_language(query, supabase, user_id, language_code)
            
        elif query.data == "voice_settings_back":
            await show_voice_settings(query, supabase, user_id)

    # --- ФУНКЦИИ ДЛЯ РАБОТЫ С ГОЛОСОВЫМИ НАСТРОЙКАМИ ---

    async def show_voice_settings(query, supabase, user_id):
        """Показывает настройки голосовых сообщений."""
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        voice_stats = await db.get_voice_stats(supabase, user_id)
        
        # Найдем название выбранного голоса
        current_voice_name = "Не найден"
        for name, voice_id in AVAILABLE_VOICES.items():
            if voice_id == voice_settings.get('selected_voice'):
                current_voice_name = name
                break
        
        # Найдем название выбранного языка
        current_language_name = "Не найден"
        for name, lang_code in AVAILABLE_LANGUAGES.items():
            if lang_code == voice_settings.get('voice_language', 'ru'):
                current_language_name = name
                break
        
        status = "🔊 Включены" if voice_settings.get('voice_enabled') else "🔇 Выключены"
        
        settings_text = (
            f"🎙️ **Настройки голосовых сообщений**\n\n"
            f"**Статус:** {status}\n"
            f"**Текущий голос:** {current_voice_name}\n"
            f"**Язык распознавания:** {current_language_name}\n\n"
            f"📊 **Статистика:**\n"
            f"• Отправлено голосовых: {voice_stats['sent']}\n"
            f"• Получено голосовых: {voice_stats['received']}\n\n"
            f"💰 **Стоимость:**\n"
            f"• Распознавание: {VOICE_TO_TEXT_COST} кредитов\n"
            f"• Голосовой ответ: {TEXT_TO_VOICE_COST} кредитов\n\n"
            f"ℹ️ Отправьте голосовое сообщение для проверки!"
        )
        
        keyboard = [
            [InlineKeyboardButton(
                "🔊 Включить голосовые ответы" if not voice_settings.get('voice_enabled') else "🔇 Выключить голосовые ответы", 
                callback_data="voice_toggle"
            )],
            [InlineKeyboardButton("🎭 Сменить голос", callback_data="voice_select")],
            [InlineKeyboardButton("🌍 Язык распознавания", callback_data="voice_language")],
            [InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def toggle_voice_mode(query, supabase, user_id):
        """Переключает режим голосовых ответов."""
        voice_settings = await db.get_user_voice_settings(supabase, user_id)
        new_status = not voice_settings.get('voice_enabled', False)
        
        success = await db.set_voice_enabled(supabase, user_id, new_status)
        
        if success:
            status_text = "включены" if new_status else "выключены"
            await query.edit_message_text(
                f"✅ Голосовые ответы {status_text}!\n\n"
                f"{'🔊 Теперь бот будет отвечать голосом на ваши голосовые сообщения.' if new_status else '💬 Теперь бот будет отвечать текстом на ваши голосовые сообщения.'}\n\n"
                "Отправьте голосовое сообщение для проверки!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="voice_settings_back")
                ]])
            )
        else:
            await query.edit_message_text(
                "❌ Ошибка при изменении настроек.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="voice_settings_back")
                ]])
            )

    async def show_voice_selection(query):
        """Показывает меню выбора голоса."""
        buttons = []
        for voice_name, voice_id in AVAILABLE_VOICES.items():
            buttons.append([InlineKeyboardButton(
                voice_name, 
                callback_data=f"voice_set_{voice_id}"
            )])
        
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="voice_settings_back")])
        
        await query.edit_message_text(
            "🎭 **Выберите голос для ответов:**\n\n"
            "🎭 **Alloy** - Нейтральный голос\n"
            "🔊 **Echo** - Мужской голос\n"
            "📖 **Fable** - Британский акцент\n"
            "💎 **Onyx** - Глубокий мужской\n"
            "✨ **Nova** - Женский голос\n"
            "🌟 **Shimmer** - Мягкий женский\n\n"
            "Выберите понравившийся:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def set_user_voice(query, supabase, user_id, voice_id):
        """Устанавливает выбранный голос."""
        success = await db.set_user_voice(supabase, user_id, voice_id)
        
        if success:
            voice_name = next((name for name, vid in AVAILABLE_VOICES.items() if vid == voice_id), voice_id)
            await query.edit_message_text(
                f"✅ **Голос изменен!**\n\n"
                f"Выбранный голос: {voice_name}\n\n"
                f"Отправьте голосовое сообщение, чтобы услышать новый голос в ответе!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="voice_settings_back")
                ]])
            )
        else:
            await query.edit_message_text(
                "❌ Ошибка при смене голоса.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="voice_settings_back")
                ]])
            )

    async def show_language_selection(query):
        """Показывает меню выбора языка распознавания."""
        buttons = []
        for language_name, language_code in AVAILABLE_LANGUAGES.items():
            buttons.append([InlineKeyboardButton(
                language_name, 
                callback_data=f"voice_lang_{language_code}"
            )])
        
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="voice_settings_back")])
        
        await query.edit_message_text(
            "🌍 **Выберите язык для распознавания речи:**\n\n"
            "Выберите язык, на котором вы будете говорить в голосовых сообщениях.\n"
            "Это поможет боту точнее распознавать вашу речь:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    async def set_user_language(query, supabase, user_id, language_code):
        """Устанавливает выбранный язык распознавания."""
        success = await db.set_user_voice_language(supabase, user_id, language_code)
        
        if success:
            language_name = next((name for name, code in AVAILABLE_LANGUAGES.items() if code == language_code), language_code)
            await query.edit_message_text(
                f"✅ **Язык распознавания изменен!**\n\n"
                f"Выбранный язык: {language_name}\n\n"
                f"Теперь отправьте голосовое сообщение на этом языке для проверки!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="voice_settings_back")
                ]])
            )
        else:
            await query.edit_message_text(
                "❌ Ошибка при смене языка.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="voice_settings_back")
                ]])
            )

    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))