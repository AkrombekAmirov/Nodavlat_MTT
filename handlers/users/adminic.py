from file_service.file_read import func_qrcode, process_contract, write_qabul
from file_service.file_database.file_path import get_file_database_path
from keyboards.inline.keyboards_inline import choose_visitor
from keyboards.inline.Dictionary import faculty_file_map1
from utils.db_api.postgresql1 import file_create_
from file_service.file_path import get_file_path
from utils.db_api.core import DatabaseService
from aiogram.dispatcher import FSMContext
from data.config import engine, ADMINS
from states.button import Form
from datetime import datetime
from loader import dp, bot
from aiogram import types
from uuid import uuid4
import logging

logging.basicConfig(filename='bot.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        await bot.send_message(user_id,
                               "Sizning arizangiz tasdiqlandi! ✅\nSizning arizangizga binoan tuzilgan quyidagi shartnoma orqali to'lovni amalga oshirishingiz mumkin.")
        await func_qrcode(url=message_id, name=user_id, status=True)
        await create_file(telegram_id=user_id, faculty=faculty)
        await call.message.edit_text(f"Ariza tasdiqlandi. ✅")

    # Rad etish holati, admindan izoh so'rash
    elif action == "reject":
        await call.message.delete()
        await call.message.answer("Iltimos, rad etish sababini yozing:")
        await state.update_data(user_id=user_id)
        await Form.reason.set()  # Rad etish sababi


@dp.message_handler(state=Form.reason)
async def get_rejection_reason(message: types.Message, state: FSMContext):
    rejection_reason = message.text
    data = await state.get_data()
    user_id = data.get("user_id")
    await bot.send_message(data.get("user_id"), f"Sizning arizangiz rad etildi. ❌\nSabab: {rejection_reason}",
                           reply_markup=choose_visitor)
    await message.answer(f"Rad etish sababi foydalanuvchiga yuborildi: {rejection_reason}")
    await state.finish()


async def create_file(telegram_id, faculty):
    user_ = db.get_user_by_telegram_id(telegram_id=telegram_id)
    contract_number = db.get_max_contract_number()

    _uuid = str(uuid4())
    _ariza_uuid = str(uuid4())
    await write_qabul([[user_.name, f"{user_.faculty}", user_.passport, contract_number,
                        user_.viloyat, user_.tuman, user_.telegram_number, datetime.now().strftime("%d-%m-%Y")]])
    await func_qrcode(url=_uuid, name=user_.name, status=True)
    await process_contract(name=user_.name, faculty=user_.faculty, passport=user_.passport,
                           number=user_.telegram_number,
                           address=f"{user_.viloyat}, {user_.tuman}", contract_number=contract_number,
                           file_name=await get_file_database_path(name=faculty_file_map1.get(faculty)))
    response = await dp.bot.send_document(telegram_id, types.InputFile(
        await get_file_path(name=f"file_shartnoma\\{user_.name}.pdf")))
    update_fields = {"contract_number": contract_number, "telegram_file_id": response.document.file_id,
                     "file_id": _uuid, "ariza_id": _ariza_uuid, "status": "True"}
    db.update_(telegram_id=telegram_id, updated_fields=update_fields)
    with open(await get_file_path(name=f"file_shartnoma\\{user_.name}.pdf"), "rb") as file:
        await file_create_(user_id=[f"{user_.passport}", _uuid, contract_number],
                           images=[(file, "application/pdf")])
    with open(await get_file_path(name=f"file_ariza\\{user_.name}.pdf"), "rb") as file:
        await file_create_(user_id=[f"{user_.passport}", _ariza_uuid, contract_number],
                           images=[(file, "application/pdf")])
    file_content = types.InputFile(await get_file_database_path(name='qabul.xlsx'))
    # await dp.bot.send_document(ADMINS, file_content)
    await dp.bot.send_document(ADMINS, response.document.file_id)
    await dp.bot.send_document(ADMINS, user_.telegram_ariza_id)
    await dp.bot.send_message(ADMINS,
                              f"F.I.Sh:<b>{user_.name}</b>\nPassport:<b>{user_.passport}</b>\nShartnoma raqami:<b>{user_.contract_number}</b>\nFakultet:<b>{user_.faculty}</b>\nTelegram raqami:{user_.telegram_number}\nViloyat:{user_.viloyat}\nTuman:{user_.tuman}")
