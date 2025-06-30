# streaming.py

import asyncio
import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import RetryAfter, BadRequest
from translations import get_text

class StreamingResponse:
    """Класс для управления потоковыми ответами от AI."""
    
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_language: str):
        self.update = update
        self.context = context
        self.user_language = user_language
        self.current_message = None
        self.buffer = ""
        self.last_update_time = 0
        self.update_interval = 1.5  # Минимальный интервал между обновлениями (секунды)
        self.final_message = ""
        
    async def start_streaming(self, initial_text: str = None):
        """Инициализирует потоковый ответ."""
        try:
            if initial_text is None:
                initial_text = get_text(self.user_language, 'streaming_thinking', default="🤖 Генерирую ответ...")
            
            self.current_message = await self.update.message.reply_text(initial_text)
            self.last_update_time = time.time()
            print(f"🎬 Начат streaming для пользователя {self.update.effective_user.id}")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации streaming: {e}")
            return False
    
    async def update_message(self, new_chunk: str, force_update: bool = False):
        """Обновляет сообщение новым куском текста."""
        if not self.current_message:
            return False
            
        self.buffer += new_chunk
        current_time = time.time()
        
        # Обновляем только если прошло достаточно времени или принудительно
        if force_update or (current_time - self.last_update_time) >= self.update_interval:
            await self._safe_update_message(self.buffer)
            self.last_update_time = current_time
            
    async def finalize_message(self, final_text: str = None, add_credits_info: bool = True, credits_cost: int = 1):
        """Завершает потоковый ответ финальным сообщением."""
        if final_text:
            self.final_message = final_text
        else:
            self.final_message = self.buffer
            
        # Добавляем информацию о кредитах
        if add_credits_info and credits_cost > 0:
            credits_text = get_text(
                self.user_language, 'streaming_credits_deducted', 
                cost=credits_cost,
                default=f"\n\n💰 Списано {credits_cost} кредитов"
            )
            self.final_message += credits_text
            
        # Финальное обновление
        await self._safe_update_message(self.final_message)
        print(f"✅ Streaming завершен для пользователя {self.update.effective_user.id}")
        
    async def _safe_update_message(self, text: str):
        """Безопасно обновляет сообщение с обработкой ошибок."""
        if not self.current_message or not text.strip():
            return False
            
        try:
            # Обрезаем текст до лимита Telegram (4096 символов)
            if len(text) > 4000:  # Оставляем запас для эмодзи и кредитов
                text = text[:4000] + "..."
                
            await self.current_message.edit_text(text)
            return True
            
        except RetryAfter as e:
            # Telegram просит подождать
            print(f"⏳ RetryAfter: ждем {e.retry_after} секунд")
            await asyncio.sleep(e.retry_after + 0.1)
            try:
                await self.current_message.edit_text(text)
                return True
            except Exception as retry_error:
                print(f"❌ Ошибка после RetryAfter: {retry_error}")
                return False
                
        except BadRequest as e:
            # Сообщение не изменилось или другая ошибка
            if "message is not modified" in str(e).lower():
                return True  # Это нормально
            print(f"❌ BadRequest при обновлении: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка при обновлении сообщения: {e}")
            return False

async def stream_openai_response(openai_client, messages, model, streaming_handler: StreamingResponse):
    """
    Получает потоковый ответ от OpenAI и передает его в StreamingHandler.
    
    Args:
        openai_client: Клиент OpenAI
        messages: Сообщения для API
        model: Модель для использования
        streaming_handler: Обработчик потокового ответа
    
    Returns:
        str: Полный ответ от AI
    """
    try:
        print("🔄 Запрашиваю потоковый ответ от OpenAI...")
        
        # Создаем потоковый запрос
        stream = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            max_tokens=1000  # Ограничиваем для потокового ответа
        )
        
        full_response = ""
        word_buffer = ""
        
        for chunk in stream:
            # Получаем кусок текста
            if chunk.choices[0].delta.content is not None:
                chunk_text = chunk.choices[0].delta.content
                full_response += chunk_text
                word_buffer += chunk_text
                
                # Обновляем каждые несколько слов для плавности
                if len(word_buffer.split()) >= 3 or chunk_text in ['.', '!', '?', '\n']:
                    await streaming_handler.update_message(word_buffer)
                    word_buffer = ""
                    
                    # Небольшая задержка для читаемости
                    await asyncio.sleep(0.1)
        
        # Обновляем остатки
        if word_buffer:
            await streaming_handler.update_message(word_buffer, force_update=True)
            
        print(f"✅ Получен полный ответ ({len(full_response)} символов)")
        return full_response
        
    except Exception as e:
        print(f"❌ Ошибка при получении потокового ответа: {e}")
        # В случае ошибки делаем обычный запрос
        try:
            print("🔄 Переключаемся на обычный режим...")
            response = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as fallback_error:
            print(f"❌ Ошибка в fallback режиме: {fallback_error}")
            return "Извините, произошла ошибка при генерации ответа."