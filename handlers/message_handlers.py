# handlers/message_handlers.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from openai import OpenAI
from config import CHAT_MODES, MESSAGE_COST, IMAGE_COST
from database import db

# ИСПРАВЛЕНО: Принимаем supabase
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, client: OpenAI, supabase):
    chat_id = update.effective_chat.id
    prompt = update.message.text
    
    current_credits = await db.get_user_credits(supabase, chat_id)
    if current_credits < IMAGE_COST:
        await update.message.reply_text(f"Недостаточно кредитов. Нужно: {IMAGE_COST}, у вас: {current_credits}.")
        await db.set_user_state(supabase, chat_id, "chat")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action='upload_photo')
    try:
        response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
        image_url = response.data[0].url
        await db.deduct_user_credits(supabase, chat_id, IMAGE_COST)
        await update.message.reply_photo(photo=image_url, caption=f"Изображение готово! Списано {IMAGE_COST} кредитов.")
    except Exception as e:
        print(f"Ошибка DALL-E: {e}")
        await update.message.reply_text("Не удалось создать изображение. Кредиты не списаны.")
    finally:
        await db.set_user_state(supabase, chat_id, "chat")

async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE, client: OpenAI, supabase):
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    current_credits = await db.get_user_credits(supabase, chat_id)
    if current_credits < MESSAGE_COST:
        await update.message.reply_text(f"У вас закончились кредиты. Для ответа нужно: {MESSAGE_COST}.")
        return

    user = await db.get_user_data(supabase, chat_id)
    current_mode_name = user['mode']
    current_model = user['model']
    history = await db.get_user_history(supabase, chat_id)
    system_prompt = CHAT_MODES.get(current_mode_name, "Ты — полезный ассистент.")
    messages_for_api = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message_text}]

    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    try:
        response = client.chat.completions.create(model=current_model, messages=messages_for_api)
        ai_response_text = response.choices[0].message.content
        
        await db.deduct_user_credits(supabase, chat_id, MESSAGE_COST)
        await db.add_message_to_history(supabase, chat_id, "user", message_text)
        await db.add_message_to_history(supabase, chat_id, "assistant", ai_response_text)
        await update.message.reply_text(ai_response_text)
    except Exception as e:
        print(f"Ошибка OpenAI Chat: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Кредиты не списаны.")

# ИСПРАВЛЕНО: Принимаем client и supabase
def register_handlers(application, client: OpenAI, supabase):
    async def main_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        
        user = await db.get_user_data(supabase, chat_id)
        if not user:
            await db.add_or_update_user(supabase, chat_id)
            user = await db.get_user_data(supabase, chat_id)

        state = user.get("state", "chat")
        if state == "awaiting_image_prompt":
            await generate_image(update, context, client, supabase)
        else:
            await chat_with_ai(update, context, client, supabase)
            
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_message_router))