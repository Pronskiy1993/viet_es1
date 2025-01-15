from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

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

# Клавиатура для подписки
sub_kb = [
    [InlineKeyboardButton(text='1 Day: 100K VND', callback_data='sub1day')],
    [InlineKeyboardButton(text='7 Days: 400K VND', callback_data='sub7days')],
    [InlineKeyboardButton(text='1 Month: 1M VND', callback_data='sub1month')],
    [InlineKeyboardButton(text='FOREVER: 10M VND', callback_data='subForever')],
    [InlineKeyboardButton(text='Free Plan: 1 Day (FREE)', callback_data='free_plan')],
]
sub_keyboard = InlineKeyboardMarkup(inline_keyboard=sub_kb)
