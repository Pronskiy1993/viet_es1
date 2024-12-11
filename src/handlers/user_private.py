import asyncio

from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.formatting import as_list, as_marked_section, Bold

from src.common.keyboards import start_kb, sub_keyboard

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start(message: types.Message):
    start_text = '🔥 Hello! I am a bot that helps find a prostitute in any city in Vietnam.\n❗ All information is confidential and private for you.\n🌶️ We make life easier.'

    print('bot started')
    await message.answer(start_text, reply_markup=start_kb)


@user_private_router.message(F.text.lower() == "instruction")
@user_private_router.message(Command("Instruction"))
async def instruction(message: types.Message):

    text = as_marked_section(
        Bold('Instruction:'),
        "Click 'Choose a girl', choose a city and district where it is convenient for you",
        "Choose a girl, under her photo there will be a phone number (SMS or Zalo) to which you need to write, date, time and duration",
        "You will receive the name of the hotel and the room where the girl you have chosen will be waiting for you",
        "Payment after. Enjoy!",
        marker="• "
    )
    await message.answer(text.as_html())
    # удаление последнего сообщения
    # new_msg = await message.answer(text.as_html())
    #
    # await asyncio.sleep(5)
    # try:
    #     await new_msg.delete()
    # except Exception:
    #     pass

@user_private_router.message(F.text.lower() == "subscribe")
async def instruction(message: types.Message):
    await message.answer('Subscribe options: ', reply_markup=sub_keyboard)

@user_private_router.message(Command("sub"))
async def go(message: types.Message):
    await message.answer('Subscribe info: ')

@user_private_router.message(Command("go"))
async def go(message: types.Message):
    await message.answer('GO!')

# @user_private_router.message(F.text)
# async def go(message: types.Message):
#     await message.answer('HZ')
