from aiogram.types import Message, URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardRemove
from aiogram.types.web_app_info import WebAppInfo
from aiogram import types

# --- Start Menu ---
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сhoose a girl", web_app=WebAppInfo(url='https://gaigu26.tv/gai-goi')),
        ],
        [
            KeyboardButton(text="Instruction"),
            KeyboardButton(text="Subscribe", callback_data="subscribe")
        ],
    ],
    resize_keyboard=True,
    # input_field_placeholder='What?'
)

# --- Delete Keyboard ---

del_kb = ReplyKeyboardRemove()

# --- Subscribe Inline Buttons ---

sub_kb = [
    [
        InlineKeyboardButton(text='1 Day: 100K VND', callback_data='sub1day'),
    ],
    [
        InlineKeyboardButton(text='7 Days: 400K VND', callback_data='sub7days'),
    ],
    [
        InlineKeyboardButton(text='1 Month: 1M VND', callback_data='sub1month'),
    ],
    [
        InlineKeyboardButton(text='FOREVER: 10M VND', callback_data='subForever'),
    ],
]
sub_keyboard = types.InlineKeyboardMarkup(inline_keyboard=sub_kb)
