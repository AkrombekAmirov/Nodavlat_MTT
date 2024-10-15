from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline import choose_visitor, keyboard
from aiogram.types import Message
from loader import dp
from data.config import engine
from utils.db_api.core import DatabaseService

db = DatabaseService(engine=engine)


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    if db.get_user_by_telegram_id(str(message.from_user.id)):
        await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)
    else:
        await message.answer("Telegram botiga xush kelibsiz.\nTelegram raqamingizni yuboring.", reply_markup=keyboard)
