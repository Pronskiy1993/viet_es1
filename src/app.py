import asyncio
import os
import json
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.utils.formatting import as_marked_section, Bold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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

# --- Подключение к базе данных ---
def get_db_connection():
    conn = sqlite3.connect('subscriptions.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для создания или обновления таблицы базы данных
def create_or_update_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Создаем таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        paid_date TEXT,
        expiry_date TEXT,
        free_used BOOLEAN DEFAULT 0
    )
    """)

    # Проверяем, есть ли столбец free_used
    try:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN free_used BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise

    conn.commit()
    conn.close()

# Функция для получения информации о подписке
def get_subscription(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,))
    subscription = cursor.fetchone()
    conn.close()
    return subscription

# Функция для обновления подписки
def update_subscription(user_id, paid_date, expiry_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO subscriptions (user_id, paid_date, expiry_date, free_used)
    VALUES (?, ?, ?, COALESCE((SELECT free_used FROM subscriptions WHERE user_id = ?), 0))
    """, (user_id, paid_date, expiry_date, user_id))
    conn.commit()
    conn.close()

# --- Загружаем локализации ---
def load_locale(language: str):
    try:
        with open(f"{LOCALES_PATH}/{language}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# --- Клавиатуры ---
# Клавиатура выбора языка
language_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="English")],
        [KeyboardButton(text="Français")],
    ],
    resize_keyboard=True,
)

# Функция для создания клавиатуры основного меню
def create_main_menu(locale):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=locale.get("choose_girl", "Choose a girl"),
                    web_app=WebAppInfo(url='https://gaigu26.tv/gai-goi')
                )
            ],
            [
                KeyboardButton(text=locale.get("instruction", "Instruction")),
                KeyboardButton(text=locale.get("subscribe", "Subscribe"))
            ],
            [
                KeyboardButton(text=locale.get("my_subscription", "My Subscription"))  # Новая кнопка
            ],
        ],
        resize_keyboard=True,
    )

# --- Обработчик команды /start ---
@user_private_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    start_text = (
        "🔥 Hello! I am a bot that helps find a prostitute in any city in Vietnam.\n"
        "❗ All information is confidential and private for you.\n"
        "🌶️ We make life easier."
    )
    await state.set_state(BotStates.choosing_language)
    await message.answer(start_text, reply_markup=language_kb)

# --- Обработчик выбора языка ---
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

# --- Обработчик основного меню ---
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

# --- Обработчик меню подписки ---
sub_kb = [
    [InlineKeyboardButton(text='1 Day: 100K VND', callback_data='sub1day')],
    [InlineKeyboardButton(text='7 Days: 400K VND', callback_data='sub7days')],
    [InlineKeyboardButton(text='1 Month: 1M VND', callback_data='sub1month')],
    [InlineKeyboardButton(text='FOREVER: 10M VND', callback_data='subForever')],
    [InlineKeyboardButton(text='Free Plan: 1 Day (FREE)', callback_data='free_plan')],
]
sub_keyboard = InlineKeyboardMarkup(inline_keyboard=sub_kb)

@user_private_router.callback_query(BotStates.subscription_menu)
async def subscription_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    user_id = callback_query.from_user.id
    today = datetime.now().strftime('%Y-%m-%d')

    subscription = get_subscription(user_id)

    if data == "free_plan":
        if subscription and subscription["free_used"]:
            await callback_query.answer("You have already used the free plan.")
        else:
            expiry_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            update_subscription(user_id, today, expiry_date)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE subscriptions SET free_used = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            await callback_query.answer("You have activated the free plan for 1 day.")
    elif data == "sub1day":
        expiry_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        update_subscription(user_id, today, expiry_date)
        await callback_query.answer("You have selected a 1-day subscription for 100K VND.")
    elif data == "sub7days":
        expiry_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        update_subscription(user_id, today, expiry_date)
        await callback_query.answer("You have selected a 7-day subscription for 400K VND.")
    elif data == "sub1month":
        expiry_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        update_subscription(user_id, today, expiry_date)
        await callback_query.answer("You have selected a 1-month subscription for 1M VND.")
    elif data == "subForever":
        expiry_date = "Forever"
        update_subscription(user_id, today, expiry_date)
        await callback_query.answer("You have selected a FOREVER subscription for 10M VND.")

    await state.set_state(BotStates.main_menu)

# --- Главная функция для запуска бота ---
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



