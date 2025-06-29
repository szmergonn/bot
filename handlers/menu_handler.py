# handlers/menu_handler.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import CHAT_MODES, AVAILABLE_MODELS
from database import db

# ИСПРАВЛЕНО: Принимаем клиент supabase
def register_handlers(application, supabase):

    def build_main_menu():
        buttons = [
            [InlineKeyboardButton("🗣️ Режим общения", callback_data="submenu_modes")],
            [InlineKeyboardButton("🧠 Выбрать модель", callback_data="submenu_models")],
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

    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))