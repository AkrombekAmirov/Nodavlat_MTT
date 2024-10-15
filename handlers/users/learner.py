from keyboards.inline import keyboard, yonalish_nomi_keyboard, response_keyboard, uzbekistan_viloyatlar, choose_visitor, \
    choose_contract_, seria_keyboard, number_keyboard, list_regioin, list_tuman, list_region1
from file_service.file_read import process_document, process_contract, func_qrcode, write_qabul
from file_service.file_database.file_path import get_file_database_path
from data.config import ADMINS, ADMIN_M1, ADMIN_M2
from file_service.file_path import get_file_path
from keyboards.inline import inline_tumanlar
from aiogram.dispatcher import FSMContext
from utils.db_api.postgresql1 import *
from states.button import Learning
from datetime import datetime
from aiogram import types
from uuid import uuid4
from loader import dp
import logging
import re
from utils.db_api.core import DatabaseService
from data.config import engine

db = DatabaseService(engine=engine)

logging.basicConfig(filename='bot.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

list_ = ["Maktabgacha ta’lim tashkiloti tarbiyachisi", "Maktabgacha ta’lim tashkiloti tarbiyachisi",
         "Defektologiya (logopediya)", "Amaliy psixologiya"]


# @dp.message_handler(commands=['start'])
# async def exit_system(message: types.Message, state: FSMContext):
#     await state.reset_state(with_data=True)  # Holatni tozalash
#     await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def test(message: types.Message, state: FSMContext):
    db.add_user(telegram_id=str(message.from_user.id), name=message.from_user.full_name,
                username=message.from_user.username,
                telegram_number=message.contact.phone_number)
    await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)


@dp.callback_query_handler(text="registration")
async def registration(call: types.CallbackQuery):
    await call.message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)
