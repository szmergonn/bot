# handlers/message_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from openai import OpenAI
from config import CHAT_MODES, MESSAGE_COST, IMAGE_COST
from database import db
from translations import get_text

# ИСПРАВЛЕНО: Принимаем supabase
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, client: OpenAI, supabase):
    chat_id = update.effective_chat.id
    prompt = update.message.text
    
    # Получаем язык пользователя
    user_language = await db.get_user_language(supabase, chat_id)
    
    current_credits = await db.get_user_credits(supabase, chat_id)
    if current_credits < IMAGE_COST:
        error_message = get_text(user_language, 'insufficient_credits_image', needed=IMAGE_COST, current=current_credits)
        await update.message.reply_text(error_message)
        await db.set_user_state(supabase, chat_id, "chat")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action='upload_photo')
    try:
        response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        image_url = response.data[0].url
        await db.deduct_user_credits(supabase, chat_id, IMAGE_COST)
        
        success_message = get_text(user_language, 'image_ready', cost=IMAGE_COST)
        await update.message.reply_photo(photo=image_url, caption=success_message)
    except Exception as e:
        print(f"Ошибка DALL-E: {e}")
        error_message = get_text(user_language, 'image_error')
        await update.message.reply_text(error_message)
    finally:
        await db.set_user_state(supabase, chat_id, "chat")

async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE, client: OpenAI, supabase):
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    # Получаем язык пользователя
    user_language = await db.get_user_language(supabase, chat_id)
    
    current_credits = await db.get_user_credits(supabase, chat_id)
    if current_credits < MESSAGE_COST:
        error_message = get_text(user_language, 'insufficient_credits_chat', cost=MESSAGE_COST)
        await update.message.reply_text(error_message)
        return

    user = await db.get_user_data(supabase, chat_id)
    current_mode_name = user['mode']
    current_model = user['model']
    streaming_enabled = user.get('streaming_enabled', True)
    history = await db.get_user_history(supabase, chat_id)
    
    # ОБНОВЛЕНО: Используем многоязычный системный промпт
    from config import get_system_prompt
    system_prompt = get_system_prompt(current_mode_name, user_language)
    
    messages_for_api = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message_text}]

    # НОВОЕ: Проверяем, включены ли потоковые ответы
    if streaming_enabled:
        await chat_with_ai_streaming(update, context, client, supabase, messages_for_api, current_model, user_language, message_text)
    else:
        await chat_with_ai_regular(update, context, client, supabase, messages_for_api, current_model, user_language, message_text)

async def chat_with_ai_streaming(update: Update, context: ContextTypes.DEFAULT_TYPE, client: OpenAI, supabase, messages_for_api, model, user_language, original_message):
    """Обрабатывает чат с AI в потоковом режиме."""
    chat_id = update.effective_chat.id
    
    try:
        # Инициализируем потоковый ответ
        from streaming import StreamingResponse, stream_openai_response
        streaming_handler = StreamingResponse(update, context, user_language)
        
        # Запускаем потоковый ответ
        success = await streaming_handler.start_streaming()
        if not success:
            # Fallback на обычный режим
            await chat_with_ai_regular(update, context, client, supabase, messages_for_api, model, user_language, original_message)
            return
        
        # Получаем потоковый ответ от OpenAI
        ai_response_text = await stream_openai_response(client, messages_for_api, model, streaming_handler)
        
        # Завершаем потоковый ответ
        await streaming_handler.finalize_message(
            final_text=ai_response_text,
            add_credits_info=True,
            credits_cost=MESSAGE_COST
        )
        
        # Списываем кредиты и сохраняем в историю
        await db.deduct_user_credits(supabase, chat_id, MESSAGE_COST)
        await db.add_message_to_history(supabase, chat_id, "user", original_message)
        await db.add_message_to_history(supabase, chat_id, "assistant", ai_response_text)
        
    except Exception as e:
        print(f"❌ Ошибка в потоковом режиме: {e}")
        # Fallback на обычный режим
        await chat_with_ai_regular(update, context, client, supabase, messages_for_api, model, user_language, original_message)

async def chat_with_ai_regular(update: Update, context: ContextTypes.DEFAULT_TYPE, client: OpenAI, supabase, messages_for_api, model, user_language, original_message):
    """Обрабатывает чат с AI в обычном режиме."""
    chat_id = update.effective_chat.id
    
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    try:
        response = client.chat.completions.create(model=model, messages=messages_for_api)
        ai_response_text = response.choices[0].message.content
        
        await db.deduct_user_credits(supabase, chat_id, MESSAGE_COST)
        await db.add_message_to_history(supabase, chat_id, "user", original_message)
        await db.add_message_to_history(supabase, chat_id, "assistant", ai_response_text)
        await update.message.reply_text(ai_response_text)
    except Exception as e:
        print(f"Ошибка OpenAI Chat: {e}")
        error_message = get_text(user_language, 'chat_error')
        await update.message.reply_text(error_message)

# ИСПРАВЛЕНО: Принимаем client и supabase
def register_handlers(application, client: OpenAI, supabase):
    async def main_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        
        user = await db.get_user_data(supabase, chat_id)
        if not user:
            # Если пользователя нет, создаем с автоопределением языка
            user_language_code = update.effective_user.language_code
            await db.add_or_update_user(supabase, chat_id, language_code=user_language_code)
            user = await db.get_user_data(supabase, chat_id)

        state = user.get("state", "chat")
        if state == "awaiting_image_prompt":
            await generate_image(update, context, client, supabase)
        else:
            await chat_with_ai(update, context, client, supabase)
            
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_message_router))