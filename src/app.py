import asyncio
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common.keyboards import language_kb, create_main_menu, sub_keyboard # Импорт клавиатур
from common.database import create_or_update_database, get_subscription, update_subscription  # Импорт работы с БД
# Импорт работы с БД

# --- Загружаем переменные окружения ---
load_dotenv()

LOCALES_PATH = 'locales'
token = os.getenv('BOT_TOKEN')

# --- Инициализация бота и диспетчера ---
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_private_router = Router()

# --- Определяем состояния FSM ---
class BotStates(StatesGroup):
    choosing_language = State()  # Состояние выбора языка
    main_menu = State()  # Состояние основного меню
    subscription_menu = State()  # Состояние меню подписки

# --- Загружаем локализации ---
def load_locale(language: str):
    try:
        with open(f"{LOCALES_PATH}/{language}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# --- Обработчики ---
@user_private_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    start_text = (
        "🔥 Hello! I am a bot that helps find a prostitute in any city in Vietnam.\n"
        "❗ All information is confidential and private for you.\n"
        "🌶️ We make life easier."
    )
    await state.set_state(BotStates.choosing_language)
    await message.answer(start_text, reply_markup=language_kb)

@user_private_router.message(BotStates.choosing_language)
async def language_selection_handler(message: Message, state: FSMContext):
    user_language = message.text.lower()
    if user_language == "english":
        language = "en"
    elif user_language == "français":
        language = "fr"
    else:
        await message.answer("Sorry, I don't support this language.")
        return

    # Сохраняем выбранный язык в FSMContext
    await state.update_data(language=language)
    locale = load_locale(language)
    welcome_message = locale.get("start_message", "Welcome to the bot!")

    # Создаём локализованную клавиатуру
    main_menu_kb = create_main_menu(locale)

    await message.answer(welcome_message, reply_markup=main_menu_kb)
    await state.set_state(BotStates.main_menu)

@user_private_router.message(BotStates.main_menu)
async def main_menu_handler(message: Message, state: FSMContext):
    state_data = await state.get_data()
    language = state_data.get("language", "en")
    locale = load_locale(language)

    if message.text.lower() == locale.get("instruction", "Instruction").lower():
        text = locale.get("instruction_text", "Instruction text is missing.")
        await message.answer(text)
    elif message.text.lower() == locale.get("subscribe", "Subscribe").lower():
        await message.answer(locale.get("subscribe_info", "Subscribe options:"), reply_markup=sub_keyboard)
        await state.set_state(BotStates.subscription_menu)
    elif message.text.lower() == locale.get("my_subscription", "My Subscription").lower():
        user_id = message.from_user.id
        subscription = get_subscription(user_id)

        if subscription:
            paid_date = subscription["paid_date"]
            expiry_date = subscription["expiry_date"]

            subscription_text = (
                f"{locale.get('subscription_info', 'Here is your subscription information:')}\n"
                f"{locale.get('paid_date', 'Paid Date:')} {paid_date}\n"
                f"{locale.get('expiry_date', 'Expiry Date:')} {expiry_date}"
            )
        else:
            subscription_text = locale.get("no_subscription", "You do not have an active subscription.")

        await message.answer(subscription_text)
    else:
        await message.answer(locale.get("unknown_command", "Sorry, I don't understand this command."))

@user_private_router.callback_query(BotStates.subscription_menu)
async def subscription_handler(callback_query: types.CallbackQuery, state: FSMContext):
    # (логика из оригинального кода)
    pass

async def main():
    create_or_update_database()
    await bot.set_my_commands([{"command": "/start", "description": "Start the bot"}])
    dp.include_router(user_private_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")

