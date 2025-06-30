# translations.py

# Словари переводов для разных языков
TRANSLATIONS = {
    'ru': {
        # Основные команды
        'welcome_message': "Привет, {user}! Я твой AI-ассистент.\n\nИспользуй /menu, чтобы выбрать режим.\nИспользуй /balance, чтобы проверить баланс кредитов.\nИспользуй /profile, чтобы открыть личный кабинет.",
        'welcome_back': "С возвращением, {user}!",
        'balance_info': "💰 У вас на балансе: {credits} кредитов.",
        
        # Меню
        'main_menu': "Главное меню:",
        'chat_mode': "🗣️ Режим общения",
        'select_model': "🧠 Выбрать модель", 
        'voice_messages': "🎙️ Голосовые сообщения",
        'generate_image': "🖼️ Сгенерировать изображение",
        'language_settings': "🌍 Язык интерфейса",
        'back': "⬅️ Назад",
        'back_to_menu': "⬅️ Назад в меню",
        
        # Режимы чата (локализованные названия)
        'chat_mode_assistant': "Помощник",
        'chat_mode_joker': "Шутник", 
        'chat_mode_translator': "Переводчик",
        
        # Модели
        'select_model_menu': "Выберите модель для общения:",
        'model_changed': "Модель изменена на: *{model}*. Возвращаю в главное меню...",
        
        # Изображения
        'image_prompt_request': "Отлично! Присылайте текстовый запрос для создания картинки.",
        'insufficient_credits_image': "Недостаточно кредитов. Нужно: {needed}, у вас: {current}.",
        'image_ready': "Изображение готово! Списано {cost} кредитов.",
        'image_error': "Не удалось создать изображение. Кредиты не списаны.",
        
        # Голосовые сообщения
        'voice_settings_title': "🎙️ **Настройки голосовых сообщений**",
        'voice_status': "**Статус:** {status}",
        'voice_enabled': "🔊 Включены",
        'voice_disabled': "🔇 Выключены", 
        'current_voice': "**Текущий голос:** {voice}",
        'recognition_language': "**Язык распознавания:** {language}",
        'voice_statistics': "📊 **Статистика:**",
        'voice_sent': "• Отправлено голосовых: {count}",
        'voice_received': "• Получено голосовых: {count}",
        'voice_costs': "💰 **Стоимость:**",
        'voice_recognition_cost': "• Только распознавание: {cost} кредитов",
        'voice_response_cost': "• Голосовой ответ: {cost} кредитов (распознавание + синтез + AI)",
        'voice_credit_warning': "⚠️ **Важно:** Для голосовых ответов нужно минимум {cost} кредитов!",
        'voice_test_hint': "ℹ️ Отправьте голосовое сообщение для проверки!",
        'voice_toggle_enable': "🔊 Включить голосовые ответы",
        'voice_toggle_disable': "🔇 Выключить голосовые ответы",
        'change_voice': "🎭 Сменить голос",
        'voice_recognition_lang': "🌍 Язык распознавания",
        
        # Сообщения голосовых
        'voice_enabled_success': "✅ Голосовые ответы включены!\n\n🔊 Теперь бот будет отвечать голосом на ваши голосовые сообщения.\n\nОтправьте голосовое сообщение для проверки!",
        'voice_disabled_success': "✅ Голосовые ответы выключены!\n\n💬 Теперь бот будет отвечать текстом на ваши голосовые сообщения.\n\nОтправьте голосовое сообщение для проверки!",
        'voice_change_error': "❌ Ошибка при изменении настроек.",
        'voice_changed_success': "✅ **Голос изменен!**\n\nВыбранный голос: {voice}\n\nОтправьте голосовое сообщение, чтобы услышать новый голос в ответе!",
        'voice_change_error_voice': "❌ Ошибка при смене голоса.",
        'language_changed_success': "✅ **Язык распознавания изменен!**\n\nВыбранный язык: {language}\n\nТеперь отправьте голосовое сообщение на этом языке для проверки!",
        'language_change_error': "❌ Ошибка при смене языка.",
        
        # Обработка голосовых
        'recognizing_speech': "🎙️ Распознаю речь...",
        'recognized_text': "🎙️ **Распознанный текст:**\n{text}\n\n💰 Списано {cost} кредитов",
        'generating_voice_response': "🔊 Генерирую голосовой ответ...",
        'voice_response_caption': "🔊 Голосовой ответ\n💰 Списано {cost} кредитов",
        'insufficient_credits_voice_full': "⚠️ **Недостаточно кредитов для голосового ответа**\n\n💰 **У вас:** {current} кредитов\n🎙️ **Нужно для голосового ответа:** {needed} кредитов\n\n💡 **Варианты:**\n• Отключите голосовые ответы в /menu → 🎙️ Голосовые сообщения\n• Пополните баланс у администратора\n• Я могу распознать речь и ответить текстом за {recognition_cost} кредитов",
        'insufficient_credits_voice_recognition': "❌ **Недостаточно кредитов для {operation}**\n\n💰 **У вас:** {current} кредитов\n🎙️ **Нужно:** {needed} кредитов\n\n💡 Обратитесь к администратору для пополнения баланса.",
        'voice_too_long': "❌ Голосовое сообщение слишком длинное!\nМаксимум: {max_duration} секунд, у вас: {duration} секунд",
        'voice_recognition_error': "❌ Не удалось распознать речь. Попробуйте еще раз.\nКредиты не были списаны.",
        'voice_generation_error': "❌ Не удалось сгенерировать голосовой ответ.\nПопробуйте текстовый режим.",
        'text_response_error': "❌ Не удалось сгенерировать ответ. Попробуйте еще раз.\nКредиты не были списаны.",
        
        # Профиль
        'profile_title': "👤 **Личный кабинет** - {name}",
        'profile_user_id': "**🆔 ID пользователя:** `{user_id}`",
        'profile_balance': "**💰 Баланс:** {credits} кредитов",
        'profile_referral_program': "🔗 **Реферальная программа:**",
        'profile_invited_friends': "📊 Приглашено друзей: **{count}**",
        'profile_invited_by': "👥 Вас пригласил: `{user_id}`",
        'profile_referral_link': "**Ваша реферальная ссылка:**\n`{link}`",
        'profile_how_it_works': "💡 **Как это работает:**\n• Поделитесь ссылкой с друзьями\n• Они получат +2 кредита при регистрации\n• Вы получите +5 кредитов за каждого друга\n\n🎯 Приглашайте больше друзей и получайте больше кредитов!",
        'profile_not_found': "❌ Не удалось найти ваш профиль. Попробуйте /start.",
        
        # Реферальная система
        'referral_welcome': "🎉 Добро пожаловать, {user}!\n\nВы пришли по реферальной ссылке и получили бонус {bonus} кредитов!\nВсего у вас теперь кредитов: {total}\n\nИспользуйте /menu для начала работы и /profile для личного кабинета.",
        'referral_inviter_notification': "🎉 Отличные новости!\n\nПо вашей реферальной ссылке зарегистрировался новый пользователь!\nВы получили бонус {bonus} кредитов.\n\nВаш баланс: {balance} кредитов",
        'referral_invalid_code': "Привет, {user}! Я твой AI-ассистент.\n\nРеферальный код недействителен, но вы всё равно получили стартовые кредиты!\n\nИспользуй /menu, чтобы выбрать режим.\nИспользуй /profile, чтобы открыть личный кабинет.",
        'referral_own_code': "Привет, {user}! Я твой AI-ассистент.\n\nНельзя использовать собственный реферальный код 😊\n\nИспользуй /menu, чтобы выбрать режим.\nИспользуй /profile, чтобы открыть личный кабинет.",
        
        # Языки интерфейса
        'language_settings_title': "🌍 **Выберите язык интерфейса:**",
        'language_settings_hint': "Выберите язык для интерфейса бота:",
        'language_changed_interface': "✅ **Язык интерфейса изменен!**\n\nВыбранный язык: {language}\n\nТеперь бот будет общаться с вами на этом языке!",
        'language_change_interface_error': "❌ Ошибка при смене языка интерфейса.",

        # Админские команды
        'admin_welcome': "👑 **Добро пожаловать в админ-панель!**\n\n📊 **Статистика:**\n/stats - Показать статистику бота\n/user\\_info <user\\_id> - Подробная информация о пользователе\n\n💰 **Управление кредитами:**\n/add\\_credits <user\\_id> <количество> - Начислить кредиты\n/remove\\_credits <user\\_id> <количество> - Снять кредиты\n\n📢 **Рассылка:**\n/broadcast <сообщение> - Отправить всем пользователям\n\nℹ️ Используйте команды для управления ботом.",
        'admin_command_format_error': "❌ **Неверный формат команды**\n\nИспользуйте: `{command}`\n\n**Пример:** `{example}`",
        'admin_credits_positive': "❌ Количество кредитов должно быть положительным числом.",
        'admin_user_not_found': "❌ Пользователь с ID {user_id} не найден в базе данных.",
        'admin_credits_added_success': "✅ **Кредиты успешно начислены!**\n\n👤 **Пользователь:** `{user_id}`\n➕ **Начислено:** {amount} кредитов\n💰 **Было:** {old_balance} кредитов\n💰 **Стало:** {new_balance} кредитов",
        'admin_credits_removed_success': "✅ **Кредиты успешно сняты!**\n\n👤 **Пользователь:** `{user_id}`\n➖ **Снято:** {amount} кредитов\n💰 **Было:** {old_balance} кредитов\n💰 **Стало:** {new_balance} кредитов",
        'admin_balance_negative_warning': "⚠️ **Внимание:** Баланс пользователя ушел в минус!",
        'admin_credits_remove_failed': "❌ **Не удалось снять кредиты**\n\n👤 **Пользователь:** `{user_id}`\n💰 **Текущий баланс:** {current} кредитов\n➖ **Попытка снять:** {amount} кредитов\n\n💡 **Причина:** Недостаточно кредитов для снятия.\nИспользуйте `force` для принудительного снятия:\n`{command} {user_id} {amount} force`",
        'admin_user_notified_credits_added': "Вам было начислено **{amount} кредитов** администратором!\n\n💰 **Текущий баланс:** {balance} кредитов",
        'admin_user_notified_credits_removed': "С вашего счета было снято **{amount} кредитов** администратором.\n\n💰 **Текущий баланс:** {balance} кредитов",
        'admin_user_balance_negative': "⚠️ Ваш баланс ушел в минус. Обратитесь к администратору.",
        'admin_notification_failed': "⚠️ Кредиты начислены, но не удалось уведомить пользователя: {error}",
        'admin_broadcast_start': "Начинаю рассылку для {count} пользователей...",
        'admin_broadcast_complete': "Рассылка завершена! Успешно: {success}, Ошибок: {failed}",
        'admin_broadcast_no_message': "Укажите сообщение. Пример: /broadcast Привет!",
        
        # Языки
        'lang_russian': "🇷🇺 Русский",
        'lang_english': "🇺🇸 English", 
        'lang_polish': "🇵🇱 Polski",
        
        # AI чат
        'insufficient_credits_chat': "У вас закончились кредиты. Для ответа нужно: {cost}.",
        'chat_error': "Извините, произошла ошибка. Кредиты не списаны.",
        
        # Ошибки
        'user_not_found': "❌ Пользователь с ID {user_id} не найден в базе данных.",
        'command_admin_only': "Эта команда доступна только администратору.",

        # Streaming Response
        'streaming_thinking': "🤖 Генерирую ответ...",
        'streaming_credits_deducted': "\n\n💰 Списано {cost} кредитов",
        'streaming_enabled': "🔥 Потоковые ответы",
        'streaming_settings_title': "🔥 **Настройки потоковых ответов**",
        'streaming_status': "**Статус:** {status}",
        'streaming_enabled_status': "🔥 Включены",
        'streaming_disabled_status': "💬 Выключены",
        'streaming_description': "**Потоковые ответы** — это когда AI «печатает» ответ в реальном времени, слово за словом, как в ChatGPT. Это создает ощущение живого общения!",
        'streaming_toggle_enable': "🔥 Включить потоковые ответы",
        'streaming_toggle_disable': "💬 Выключить потоковые ответы",
        'streaming_enabled_success': "✅ **Потоковые ответы включены!**\n\n🔥 Теперь AI будет «печатать» ответы в реальном времени.\n\nОтправьте сообщение для проверки!",
        'streaming_disabled_success': "✅ **Потоковые ответы выключены!**\n\n💬 Теперь AI будет отправлять полные ответы сразу.\n\nОтправьте сообщение для проверки!",
        'streaming_change_error': "❌ Ошибка при изменении настроек потоковых ответов.",


        'voice_language_synced': "🎙️ **Язык голосового общения автоматически синхронизирован** с языком интерфейса",
    },
    
    'en': {
        # Основные команды
        'welcome_message': "Hello, {user}! I'm your AI assistant.\n\nUse /menu to select a mode.\nUse /balance to check your credit balance.\nUse /profile to open your account.",
        'welcome_back': "Welcome back, {user}!",
        'balance_info': "💰 Your balance: {credits} credits.",
        
        # Меню
        'main_menu': "Main menu:",
        'chat_mode': "🗣️ Chat Mode",
        'select_model': "🧠 Select Model",
        'voice_messages': "🎙️ Voice Messages", 
        'generate_image': "🖼️ Generate Image",
        'language_settings': "🌍 Interface Language",
        'back': "⬅️ Back",
        'back_to_menu': "⬅️ Back to menu",
        
        # Режимы чата (локализованные названия)
        'chat_mode_assistant': "Assistant",
        'chat_mode_joker': "Joker",
        'chat_mode_translator': "Translator",
        
        # Модели
        'select_model_menu': "Select model for communication:",
        'model_changed': "Model changed to: *{model}*. Returning to main menu...",
        
        # Изображения
        'image_prompt_request': "Great! Send a text prompt to create an image.",
        'insufficient_credits_image': "Insufficient credits. Need: {needed}, you have: {current}.",
        'image_ready': "Image ready! {cost} credits deducted.",
        'image_error': "Failed to create image. Credits were not deducted.",
        
        # Голосовые сообщения
        'voice_settings_title': "🎙️ **Voice Message Settings**",
        'voice_status': "**Status:** {status}",
        'voice_enabled': "🔊 Enabled",
        'voice_disabled': "🔇 Disabled",
        'current_voice': "**Current voice:** {voice}",
        'recognition_language': "**Recognition language:** {language}",
        'voice_statistics': "📊 **Statistics:**",
        'voice_sent': "• Voice messages sent: {count}",
        'voice_received': "• Voice messages received: {count}",
        'voice_costs': "💰 **Costs:**",
        'voice_recognition_cost': "• Recognition only: {cost} credits",
        'voice_response_cost': "• Voice response: {cost} credits (recognition + synthesis + AI)",
        'voice_credit_warning': "⚠️ **Important:** Voice responses require at least {cost} credits!",
        'voice_test_hint': "ℹ️ Send a voice message to test!",
        'voice_toggle_enable': "🔊 Enable voice responses",
        'voice_toggle_disable': "🔇 Disable voice responses",
        'change_voice': "🎭 Change voice",
        'voice_recognition_lang': "🌍 Recognition language",
        
        # Сообщения голосовых
        'voice_enabled_success': "✅ Voice responses enabled!\n\n🔊 Now the bot will respond with voice to your voice messages.\n\nSend a voice message to test!",
        'voice_disabled_success': "✅ Voice responses disabled!\n\n💬 Now the bot will respond with text to your voice messages.\n\nSend a voice message to test!",
        'voice_change_error': "❌ Error changing settings.",
        'voice_changed_success': "✅ **Voice changed!**\n\nSelected voice: {voice}\n\nSend a voice message to hear the new voice in response!",
        'voice_change_error_voice': "❌ Error changing voice.",
        'language_changed_success': "✅ **Recognition language changed!**\n\nSelected language: {language}\n\nNow send a voice message in this language to test!",
        'language_change_error': "❌ Error changing language.",
        
        # Обработка голосовых
        'recognizing_speech': "🎙️ Recognizing speech...",
        'recognized_text': "🎙️ **Recognized text:**\n{text}\n\n💰 {cost} credits deducted",
        'generating_voice_response': "🔊 Generating voice response...",
        'voice_response_caption': "🔊 Voice response\n💰 {cost} credits deducted",
        'insufficient_credits_voice_full': "⚠️ **Insufficient credits for voice response**\n\n💰 **You have:** {current} credits\n🎙️ **Need for voice response:** {needed} credits\n\n💡 **Options:**\n• Disable voice responses in /menu → 🎙️ Voice Messages\n• Top up balance with administrator\n• I can recognize speech and respond with text for {recognition_cost} credits",
        'insufficient_credits_voice_recognition': "❌ **Insufficient credits for {operation}**\n\n💰 **You have:** {current} credits\n🎙️ **Need:** {needed} credits\n\n💡 Contact administrator to top up balance.",
        'voice_too_long': "❌ Voice message too long!\nMaximum: {max_duration} seconds, yours: {duration} seconds",
        'voice_recognition_error': "❌ Failed to recognize speech. Try again.\nCredits were not deducted.",
        'voice_generation_error': "❌ Failed to generate voice response.\nTry text mode.",
        'text_response_error': "❌ Failed to generate response. Try again.\nCredits were not deducted.",
        
        # Профиль
        'profile_title': "👤 **Profile** - {name}",
        'profile_user_id': "**🆔 User ID:** `{user_id}`",
        'profile_balance': "**💰 Balance:** {credits} credits",
        'profile_referral_program': "🔗 **Referral Program:**",
        'profile_invited_friends': "📊 Friends invited: **{count}**",
        'profile_invited_by': "👥 You were invited by: `{user_id}`",
        'profile_referral_link': "**Your referral link:**\n`{link}`",
        'profile_how_it_works': "💡 **How it works:**\n• Share the link with friends\n• They get +2 credits on registration\n• You get +5 credits for each friend\n\n🎯 Invite more friends and get more credits!",
        'profile_not_found': "❌ Could not find your profile. Try /start.",
        
        # Реферальная система
        'referral_welcome': "🎉 Welcome, {user}!\n\nYou came through a referral link and received {bonus} bonus credits!\nYour total credits: {total}\n\nUse /menu to start and /profile for your account.",
        'referral_inviter_notification': "🎉 Great news!\n\nA new user registered through your referral link!\nYou received {bonus} bonus credits.\n\nYour balance: {balance} credits",
        'referral_invalid_code': "Hello, {user}! I'm your AI assistant.\n\nReferral code is invalid, but you still received starter credits!\n\nUse /menu to select a mode.\nUse /profile to open your account.",
        'referral_own_code': "Hello, {user}! I'm your AI assistant.\n\nYou cannot use your own referral code 😊\n\nUse /menu to select a mode.\nUse /profile to open your account.",
        
        # Языки интерфейса
        'language_settings_title': "🌍 **Select interface language:**",
        'language_settings_hint': "Choose language for bot interface:",
        'language_changed_interface': "✅ **Interface language changed!**\n\nSelected language: {language}\n\nNow the bot will communicate with you in this language!",
        'language_change_interface_error': "❌ Error changing interface language.",
        
        # Языки
        'lang_russian': "🇷🇺 Русский",
        'lang_english': "🇺🇸 English",
        'lang_polish': "🇵🇱 Polski",

         # Админские команды
        'admin_welcome': "👑 **Welcome to admin panel!**\n\n📊 **Statistics:**\n/stats - Show bot statistics\n/user\\_info <user\\_id> - Detailed user information\n\n💰 **Credit management:**\n/add\\_credits <user\\_id> <amount> - Add credits\n/remove\\_credits <user\\_id> <amount> - Remove credits\n\n📢 **Broadcast:**\n/broadcast <message> - Send to all users\n\nℹ️ Use commands to manage the bot.",
        'admin_command_format_error': "❌ **Invalid command format**\n\nUse: `{command}`\n\n**Example:** `{example}`",
        'admin_credits_positive': "❌ Credit amount must be a positive number.",
        'admin_user_not_found': "❌ User with ID {user_id} not found in database.",
        'admin_credits_added_success': "✅ **Credits successfully added!**\n\n👤 **User:** `{user_id}`\n➕ **Added:** {amount} credits\n💰 **Was:** {old_balance} credits\n💰 **Now:** {new_balance} credits",
        'admin_credits_removed_success': "✅ **Credits successfully removed!**\n\n👤 **User:** `{user_id}`\n➖ **Removed:** {amount} credits\n💰 **Was:** {old_balance} credits\n💰 **Now:** {new_balance} credits",
        'admin_balance_negative_warning': "⚠️ **Warning:** User balance went negative!",
        'admin_credits_remove_failed': "❌ **Failed to remove credits**\n\n👤 **User:** `{user_id}`\n💰 **Current balance:** {current} credits\n➖ **Attempted to remove:** {amount} credits\n\n💡 **Reason:** Insufficient credits for removal.\nUse `force` for forced removal:\n`{command} {user_id} {amount} force`",
        'admin_user_notified_credits_added': "You have been credited **{amount} credits** by administrator!\n\n💰 **Current balance:** {balance} credits",
        'admin_user_notified_credits_removed': "**{amount} credits** have been deducted from your account by administrator.\n\n💰 **Current balance:** {balance} credits",
        'admin_user_balance_negative': "⚠️ Your balance went negative. Contact administrator.",
        'admin_notification_failed': "⚠️ Credits added, but failed to notify user: {error}",
        'admin_broadcast_start': "Starting broadcast for {count} users...",
        'admin_broadcast_complete': "Broadcast completed! Success: {success}, Errors: {failed}",
        'admin_broadcast_no_message': "Specify message. Example: /broadcast Hello!",
        
        # AI чат
        'insufficient_credits_chat': "You've run out of credits. Need for response: {cost}.",
        'chat_error': "Sorry, an error occurred. Credits were not deducted.",
        
        # Ошибки
        'user_not_found': "❌ User with ID {user_id} not found in database.",
        'command_admin_only': "This command is only available to administrators.",

        # Streaming Response  
        'streaming_thinking': "🤖 Generating response...",
        'streaming_credits_deducted': "\n\n💰 {cost} credits deducted",
        'streaming_enabled': "🔥 Streaming responses",
        'streaming_settings_title': "🔥 **Streaming Response Settings**",
        'streaming_status': "**Status:** {status}",
        'streaming_enabled_status': "🔥 Enabled",
        'streaming_disabled_status': "💬 Disabled",
        'streaming_description': "**Streaming responses** — AI \"types\" the response in real-time, word by word, like in ChatGPT. This creates a feeling of live communication!",
        'streaming_toggle_enable': "🔥 Enable streaming responses",
        'streaming_toggle_disable': "💬 Disable streaming responses",
        'streaming_enabled_success': "✅ **Streaming responses enabled!**\n\n🔥 Now AI will \"type\" responses in real-time.\n\nSend a message to test!",
        'streaming_disabled_success': "✅ **Streaming responses disabled!**\n\n💬 Now AI will send complete responses at once.\n\nSend a message to test!",
        'streaming_change_error': "❌ Error changing streaming response settings.",

        'voice_language_synced': "🎙️ **Voice communication language automatically synchronized** with interface language",
    },
    
    'pl': {
        # Podstawowe komendy
        'welcome_message': "Cześć, {user}! Jestem twoim asystentem AI.\n\nUżyj /menu, aby wybrać tryb.\nUżyj /balance, aby sprawdzić saldo kredytów.\nUżyj /profile, aby otworzyć swoje konto.",
        'welcome_back': "Witaj ponownie, {user}!",
        'balance_info': "💰 Twoje saldo: {credits} kredytów.",
        
        # Menu
        'main_menu': "Menu główne:",
        'chat_mode': "🗣️ Tryb rozmowy",
        'select_model': "🧠 Wybierz model",
        'voice_messages': "🎙️ Wiadomości głosowe",
        'generate_image': "🖼️ Generuj obraz",
        'language_settings': "🌍 Język interfejsu",
        'back': "⬅️ Wstecz",
        'back_to_menu': "⬅️ Powrót do menu",
        
        # Tryby czatu
        'select_chat_mode': "Wybierz tryb rozmowy:",
        'mode_changed': "Tryb zmieniony na: *{mode}*. Powracam do menu głównego...",
        
        # Modele
        'select_model_menu': "Wybierz model do komunikacji:",
        'model_changed': "Model zmieniony na: *{model}*. Powracam do menu głównego...",
        
        # Obrazy
        'image_prompt_request': "Świetnie! Wyślij tekstowy opis, aby utworzyć obraz.",
        'insufficient_credits_image': "Niewystarczające kredyty. Potrzeba: {needed}, masz: {current}.",
        'image_ready': "Obraz gotowy! Pobrano {cost} kredytów.",
        'image_error': "Nie udało się utworzyć obrazu. Kredyty nie zostały pobrane.",
        
        # Wiadomości głosowe
        'voice_settings_title': "🎙️ **Ustawienia wiadomości głosowych**",
        'voice_status': "**Status:** {status}",
        'voice_enabled': "🔊 Włączone",
        'voice_disabled': "🔇 Wyłączone",
        'current_voice': "**Aktualny głos:** {voice}",
        'recognition_language': "**Język rozpoznawania:** {language}",
        'voice_statistics': "📊 **Statystyki:**",
        'voice_sent': "• Wysłane wiadomości głosowe: {count}",
        'voice_received': "• Otrzymane wiadomości głosowe: {count}",
        'voice_costs': "💰 **Koszty:**",
        'voice_recognition_cost': "• Tylko rozpoznawanie: {cost} kredytów",
        'voice_response_cost': "• Odpowiedź głosowa: {cost} kredytów (rozpoznawanie + synteza + AI)",
        'voice_credit_warning': "⚠️ **Ważne:** Odpowiedzi głosowe wymagają co najmniej {cost} kredytów!",
        'voice_test_hint': "ℹ️ Wyślij wiadomość głosową, aby przetestować!",
        'voice_toggle_enable': "🔊 Włącz odpowiedzi głosowe",
        'voice_toggle_disable': "🔇 Wyłącz odpowiedzi głosowe",
        'change_voice': "🎭 Zmień głos",
        'voice_recognition_lang': "🌍 Język rozpoznawania",
        
        # Wiadomości głosowe
        'voice_enabled_success': "✅ Odpowiedzi głosowe włączone!\n\n🔊 Teraz bot będzie odpowiadać głosem na twoje wiadomości głosowe.\n\nWyślij wiadomość głosową, aby przetestować!",
        'voice_disabled_success': "✅ Odpowiedzi głosowe wyłączone!\n\n💬 Teraz bot będzie odpowiadać tekstem na twoje wiadomości głosowe.\n\nWyślij wiadomość głosową, aby przetestować!",
        'voice_change_error': "❌ Błąd podczas zmiany ustawień.",
        'voice_changed_success': "✅ **Głos zmieniony!**\n\nWybrany głos: {voice}\n\nWyślij wiadomość głosową, aby usłyszeć nowy głos w odpowiedzi!",
        'voice_change_error_voice': "❌ Błąd podczas zmiany głosu.",
        'language_changed_success': "✅ **Język rozpoznawania zmieniony!**\n\nWybrany język: {language}\n\nTeraz wyślij wiadomość głosową w tym języku, aby przetestować!",
        'language_change_error': "❌ Błąd podczas zmiany języka.",

        # Режимы чата (локализованные названия)
        'chat_mode_assistant': "Asystent", 
        'chat_mode_joker': "Żartowniś",
        'chat_mode_translator': "Tłumacz",
        
        # Przetwarzanie głosu
        'recognizing_speech': "🎙️ Rozpoznaję mowę...",
        'recognized_text': "🎙️ **Rozpoznany tekst:**\n{text}\n\n💰 Pobrano {cost} kredytów",
        'generating_voice_response': "🔊 Generuję odpowiedź głosową...",
        'voice_response_caption': "🔊 Odpowiedź głosowa\n💰 Pobrano {cost} kredytów",
        'insufficient_credits_voice_full': "⚠️ **Niewystarczające kredyty na odpowiedź głosową**\n\n💰 **Masz:** {current} kredytów\n🎙️ **Potrzebujesz na odpowiedź głosową:** {needed} kredytów\n\n💡 **Opcje:**\n• Wyłącz odpowiedzi głosowe w /menu → 🎙️ Wiadomości głosowe\n• Doładuj saldo u administratora\n• Mogę rozpoznać mowę i odpowiedzieć tekstem za {recognition_cost} kredytów",
        'insufficient_credits_voice_recognition': "❌ **Niewystarczające kredyty na {operation}**\n\n💰 **Masz:** {current} kredytów\n🎙️ **Potrzebujesz:** {needed} kredytów\n\n💡 Skontaktuj się z administratorem, aby doładować saldo.",
        'voice_too_long': "❌ Wiadomość głosowa zbyt długa!\nMaksymalnie: {max_duration} sekund, twoja: {duration} sekund",
        'voice_recognition_error': "❌ Nie udało się rozpoznać mowy. Spróbuj ponownie.\nKredyty nie zostały pobrane.",
        'voice_generation_error': "❌ Nie udało się wygenerować odpowiedzi głosowej.\nSpróbuj trybu tekstowego.",
        'text_response_error': "❌ Nie udało się wygenerować odpowiedzi. Spróbuj ponownie.\nKredyty nie zostały pobrane.",
        
        # Profil
        'profile_title': "👤 **Profil** - {name}",
        'profile_user_id': "**🆔 ID użytkownika:** `{user_id}`",
        'profile_balance': "**💰 Saldo:** {credits} kredytów",
        'profile_referral_program': "🔗 **Program referencyjny:**",
        'profile_invited_friends': "📊 Zaproszeni znajomi: **{count}**",
        'profile_invited_by': "👥 Zostałeś zaproszony przez: `{user_id}`",
        'profile_referral_link': "**Twój link referencyjny:**\n`{link}`",
        'profile_how_it_works': "💡 **Jak to działa:**\n• Udostępnij link znajomym\n• Otrzymają +2 kredyty przy rejestracji\n• Ty otrzymasz +5 kredytów za każdego znajomego\n\n🎯 Zapraszaj więcej znajomych i zdobywaj więcej kredytów!",
        'profile_not_found': "❌ Nie można znaleźć twojego profilu. Spróbuj /start.",
        
        # System referencyjny
        'referral_welcome': "🎉 Witaj, {user}!\n\nPrzyszedłeś przez link referencyjny i otrzymałeś bonus {bonus} kredytów!\nTwoje łączne kredyty: {total}\n\nUżyj /menu, aby zacząć i /profile dla swojego konta.",
        'referral_inviter_notification': "🎉 Świetne wiadomości!\n\nNowy użytkownik zarejestrował się przez twój link referencyjny!\nOtrzymałeś bonus {bonus} kredytów.\n\nTwoje saldo: {balance} kredytów",
        'referral_invalid_code': "Cześć, {user}! Jestem twoim asystentem AI.\n\nKod referencyjny jest nieprawidłowy, ale i tak otrzymałeś początkowe kredyty!\n\nUżyj /menu, aby wybrać tryb.\nUżyj /profile, aby otworzyć swoje konto.",
        'referral_own_code': "Cześć, {user}! Jestem twoim asystentem AI.\n\nNie możesz użyć własnego kodu referencyjnego 😊\n\nUżyj /menu, aby wybrać tryb.\nUżyj /profile, aby otworzyć swoje konto.",
        
        # Języki interfejsu
        'language_settings_title': "🌍 **Wybierz język interfejsu:**",
        'language_settings_hint': "Wybierz język interfejsu bota:",
        'language_changed_interface': "✅ **Język interfejsu zmieniony!**\n\nWybrany język: {language}\n\nTeraz bot będzie komunikować się z tobą w tym języku!",
        'language_change_interface_error': "❌ Błąd podczas zmiany języka interfejsu.",
        
        # Języki
        'lang_russian': "🇷🇺 Русский",
        'lang_english': "🇺🇸 English",
        'lang_polish': "🇵🇱 Polski",

        # Админские команды
        'admin_welcome': "👑 **Witamy w panelu administratora!**\n\n📊 **Statystyki:**\n/stats - Pokaż statystyki bota\n/user\\_info <user\\_id> - Szczegółowe informacje o użytkowniku\n\n💰 **Zarządzanie kredytami:**\n/add\\_credits <user\\_id> <ilość> - Dodaj kredyty\n/remove\\_credits <user\\_id> <ilość> - Usuń kredyty\n\n📢 **Rozsyłanie:**\n/broadcast <wiadomość> - Wyślij do wszystkich użytkowników\n\nℹ️ Używaj komend do zarządzania botem.",
        'admin_command_format_error': "❌ **Nieprawidłowy format komendy**\n\nUżyj: `{command}`\n\n**Przykład:** `{example}`",
        'admin_credits_positive': "❌ Ilość kredytów musi być liczbą dodatnią.",
        'admin_user_not_found': "❌ Użytkownik o ID {user_id} nie został znaleziony w bazie danych.",
        'admin_credits_added_success': "✅ **Kredyty zostały pomyślnie dodane!**\n\n👤 **Użytkownik:** `{user_id}`\n➕ **Dodano:** {amount} kredytów\n💰 **Było:** {old_balance} kredytów\n💰 **Jest:** {new_balance} kredytów",
        'admin_credits_removed_success': "✅ **Kredyty zostały pomyślnie usunięte!**\n\n👤 **Użytkownik:** `{user_id}`\n➖ **Usunięto:** {amount} kredytów\n💰 **Było:** {old_balance} kredytów\n💰 **Jest:** {new_balance} kredytów",
        'admin_balance_negative_warning': "⚠️ **Uwaga:** Saldo użytkownika spadło poniżej zera!",
        'admin_credits_remove_failed': "❌ **Nie udało się usunąć kredytów**\n\n👤 **Użytkownik:** `{user_id}`\n💰 **Obecne saldo:** {current} kredytów\n➖ **Próba usunięcia:** {amount} kredytów\n\n💡 **Powód:** Niewystarczające kredyty do usunięcia.\nUżyj `force` dla wymuszenia:\n`{command} {user_id} {amount} force`",
        'admin_user_notified_credits_added': "Otrzymałeś **{amount} kredytów** od administratora!\n\n💰 **Obecne saldo:** {balance} kredytów",
        'admin_user_notified_credits_removed': "Z twojego konta zostało pobrane **{amount} kredytów** przez administratora.\n\n💰 **Obecne saldo:** {balance} kredytów",
        'admin_user_balance_negative': "⚠️ Twoje saldo spadło poniżej zera. Skontaktuj się z administratorem.",
        'admin_notification_failed': "⚠️ Kredyty dodane, ale nie udało się powiadomić użytkownika: {error}",
        'admin_broadcast_start': "Rozpoczynam rozsyłanie dla {count} użytkowników...",
        'admin_broadcast_complete': "Rozsyłanie zakończone! Sukces: {success}, Błędy: {failed}",
        'admin_broadcast_no_message': "Podaj wiadomość. Przykład: /broadcast Cześć!",
        
        # Chat AI
        'insufficient_credits_chat': "Skończyły ci się kredyty. Potrzebujesz na odpowiedź: {cost}.",
        'chat_error': "Przepraszamy, wystąpił błąd. Kredyty nie zostały pobrane.",
        
        # Błędy
        'user_not_found': "❌ Użytkownik o ID {user_id} nie został znaleziony w bazie danych.",
        'command_admin_only': "Ta komenda jest dostępna tylko dla administratorów.",

        # Streaming Response
        'streaming_thinking': "🤖 Generuję odpowiedź...",
        'streaming_credits_deducted': "\n\n💰 Pobrano {cost} kredytów",
        'streaming_enabled': "🔥 Odpowiedzi strumieniowe",
        'streaming_settings_title': "🔥 **Ustawienia odpowiedzi strumieniowych**",
        'streaming_status': "**Status:** {status}",
        'streaming_enabled_status': "🔥 Włączone",
        'streaming_disabled_status': "💬 Wyłączone", 
        'streaming_description': "**Odpowiedzi strumieniowe** — AI \"pisze\" odpowiedź w czasie rzeczywistym, słowo po słowie, jak w ChatGPT. To tworzy wrażenie żywej komunikacji!",
        'streaming_toggle_enable': "🔥 Włącz odpowiedzi strumieniowe",
        'streaming_toggle_disable': "💬 Wyłącz odpowiedzi strumieniowe",
        'streaming_enabled_success': "✅ **Odpowiedzi strumieniowe włączone!**\n\n🔥 Teraz AI będzie \"pisać\" odpowiedzi w czasie rzeczywistym.\n\nWyślij wiadomość, aby przetestować!",
        'streaming_disabled_success': "✅ **Odpowiedzi strumieniowe wyłączone!**\n\n💬 Teraz AI będzie wysyłać pełne odpowiedzi od razu.\n\nWyślij wiadomość, aby przetestować!",
        'streaming_change_error': "❌ Błąd podczas zmiany ustawień odpowiedzi strumieniowych.",

        'voice_language_synced': "🎙️ **Język komunikacji głosowej automatycznie zsynchronizowany** z językiem interfejsu",
    }
}

# Функция для получения перевода
def get_text(language_code: str, key: str, **kwargs) -> str:
    """
    Получает переведенный текст по ключу для указанного языка.
    
    Args:
        language_code: Код языка ('ru', 'en', 'pl')
        key: Ключ перевода
        **kwargs: Параметры для форматирования строки
    
    Returns:
        Переведенная строка
    """
    # Если язык не поддерживается, используем английский
    if language_code not in TRANSLATIONS:
        language_code = 'en'
    
    # Если ключ не найден, используем английский
    if key not in TRANSLATIONS[language_code]:
        if key in TRANSLATIONS['en']:
            language_code = 'en'
        else:
            return f"[MISSING: {key}]"
    
    text = TRANSLATIONS[language_code][key]
    
    # Форматируем строку с параметрами
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text

# Словарь языковых кодов для автоопределения
LANGUAGE_MAPPING = {
    'ru': 'ru',
    'en': 'en', 
    'pl': 'pl',
    'uk': 'ru',  # Украинский -> Русский
    'be': 'ru',  # Белорусский -> Русский
    'de': 'en',  # Немецкий -> Английский
    'fr': 'en',  # Французский -> Английский
    'es': 'en',  # Испанский -> Английский
    'it': 'en',  # Итальянский -> Английский
}

def detect_user_language(telegram_language_code: str) -> str:
    """
    Определяет язык интерфейса на основе языка Telegram пользователя.
    
    Args:
        telegram_language_code: Код языка из Telegram (например, 'ru', 'en-US', 'pl')
    
    Returns:
        Код языка интерфейса ('ru', 'en', 'pl')
    """
    if not telegram_language_code:
        return 'en'  # По умолчанию английский
    
    # Берем только первые 2 символа (ru из ru-RU)
    base_language = telegram_language_code.lower()[:2]
    
    return LANGUAGE_MAPPING.get(base_language, 'en')