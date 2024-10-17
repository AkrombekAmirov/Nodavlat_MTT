from loader import dp, bot
from datetime import datetime
from aiogram import types
from uuid import uuid4
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from states.button import Form
from keyboards.inline.keyboards_inline import choose_visitor
from file_service.file_read import func_qrcode, process_contract
from utils.db_api.core import DatabaseService
from data.config import engine
from keyboards.inline.Dictionary import faculty_file_map1
from file_service.file_database.file_path import get_file_database_path

db = DatabaseService(engine=engine)


@dp.callback_query_handler(lambda c: c.data.startswith("approve_") or c.data.startswith("reject_"))
async def process_application_response(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("_")
    action = data[0]  # "approve" yoki "reject"
    user_id = data[1]  # Foydalanuvchi ID
    message_id = data[2]  # Ariza message_id
    faculty = data[3]  # Foydalanuvchi fakulteti

    # Tasdiqlangan holat
    if action == "approve":
        await bot.send_message(user_id, "Sizning arizangiz tasdiqlandi! ✅")
        await func_qrcode(url=message_id, name=user_id, status=True)
        await create_file(telegram_id=user_id, faculty=faculty)
        await call.message.edit_text(f"Ariza tasdiqlandi. ✅ (Foydalanuvchi ID: {user_id})")

    # Rad etish holati, admindan izoh so'rash
    elif action == "reject":
        await call.message.answer("Iltimos, rad etish sababini yozing:")
        await state.update_data(user_id=user_id)
        await Form.reason.set()  # Rad etish sab


@dp.message_handler(state=Form.reason)
async def get_rejection_reason(message: types.Message, state: FSMContext):
    rejection_reason = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    await bot.send_message(user_id, f"Sizning arizangiz rad etildi. ❌\nSabab: {rejection_reason}",
                           reply_markup=choose_visitor)
    await message.answer(f"Rad etish sababi foydalanuvchiga yuborildi: {rejection_reason}")
    await state.finish()


async def create_file(telegram_id, faculty):
    user_ = db.get_user_by_telegram_id(telegram_id=telegram_id)
    contract_number = db.get_max_contract_number()
    _uuid = str(uuid4())
    await func_qrcode(url=_uuid, name=user_.name, status=True)
    await process_contract(name=user_.name, faculty=user_.faculty, passport=user_.passport, number=user_.telegram_number,
                           address=user_.address, contract_number=contract_number,
                           file_name=await get_file_database_path(name=faculty_file_map1.get(faculty)))
