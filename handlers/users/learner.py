from keyboards.inline import (
    keyboard, yonalish_nomi_keyboard, response_keyboard,
    uzbekistan_viloyatlar, choose_visitor, choose_contract_,
    seria_keyboard, number_keyboard, list_regioin,
    list_tuman, list_region1, response_admin,
    keyboard_func, inline_tumanlar
)
from file_service.file_read import process_document, process_contract, func_qrcode, write_qabul
from keyboards.inline.Dictionary import faculty_file_map, faculty_file_map2
from file_service.file_database.file_path import get_file_database_path
from data.config import ADMINS, ADMIN_M1, ADMIN_M2
from file_service.file_path import get_file_path
from utils.db_api.core import DatabaseService
from aiogram.dispatcher import FSMContext
from utils.db_api.postgresql1 import *
from states.button import Learning
from data.config import engine
from datetime import datetime
from aiogram import types
from uuid import uuid4
from loader import dp
import logging
import re

# Database service initialization
db = DatabaseService(engine=engine)

# Set up logging configuration
logging.basicConfig(
    filename='bot.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Error handler decorator
def handle_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            if isinstance(args[0], types.CallbackQuery):
                await args[0].answer("Bir xato yuz berdi, iltimos, qaytadan urinib ko'ring.")
            return None
    return wrapper



@dp.message_handler(commands=['start'])
@handle_errors
async def exit_system(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)  # Holatni tozalash
    await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)


@dp.message_handler(content_types=types.ContentType.CONTACT)
@handle_errors
async def test(message: types.Message, state: FSMContext, raw_state: FSMContext):
    user_id = str(message.from_user.id)
    if db.get_user_exists(user_id):
        await message.answer("Quyidagi no'mer bilan avval ro'yhatdan o'tilgan.\nQuyidagi xizmat turini tanlang!",
                             reply_markup=choose_visitor)
    elif message.contact.user_id == message.from_user.id:
        db.add_user(
            telegram_id=user_id,
            username=message.from_user.username or "",
            telegram_name=message.from_user.full_name,
            telegram_number=message.contact.phone_number
        )
        await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)
    else:
        await message.answer(
            "Siz yuborgan telegram kontaktangiz sizga tegishli emas!\nIltimos, o'zingizni telegram kontaktingizni yuboring")


@dp.callback_query_handler(text="registration")
@handle_errors
async def registration(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    if not db.get_user_exists(call.from_user.id):
        await call.message.answer("Telegram kontaktangizni yuboring.", reply_markup=keyboard)
    else:
        user_ = db.get_user_by_telegram_id(telegram_id=call.from_user.id)
        if user_.telegram_number:
            await call.message.delete()
            await call.message.answer("O'quv kursi yo'nalishlarini tanlang", reply_markup=yonalish_nomi_keyboard)
        else:
            await call.message.answer("Telegram kontaktangizni yuboring.", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith("faculty"))
@handle_errors
async def faculty(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    await call.message.delete()
    await state.update_data({"yonalish": call.data})
    await call.message.answer("Viloyatingizni tanlang.", reply_markup=uzbekistan_viloyatlar)


@dp.callback_query_handler(lambda call: call.data in list_regioin)
@handle_errors
async def region(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    await call.message.delete()
    await state.update_data({"region": list_region1[int(call.data[3:])]})
    await call.message.answer("Tumanlarni tanlang.", reply_markup=await inline_tumanlar(call.data))


@dp.callback_query_handler(lambda call: call.data in list_tuman)
@handle_errors
async def region(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    await call.message.delete()
    await state.update_data({"tuman": call.data})
    await call.message.answer("Familiya, Ism va Sharifingizni kiriting.")
    await Learning.zero.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Learning.zero)
@handle_errors
async def answer_name(message: types.Message, state: FSMContext, raw_state: FSMContext):
    await state.update_data({"Name": message.text})
    logging.info(f"{message.from_user.id} {message.text}")
    await message.delete()

    if message.text.startswith("/start"):
        await exit_system(message, state)
    elif re.match(r"^[A-Za-z\s']+$", message.text):
        await state.update_data({"Name": message.text})
        await message.answer("Pasportingiz seria va raqamini kiriting!", reply_markup=seria_keyboard)
        await Learning.next()
    else:
        await message.answer(
            "Siz malumot kiritishda xatolikga yo'l quydingiz! Iltimos Familiya, Ism va Sharifingizni lotin alifbosida kiriting.")
        await Learning.zero.set()


@dp.callback_query_handler(lambda call: call.data in ["AA", "AB", "AC", "AD", "AE", "KA"], state=Learning.one)
@handle_errors
async def answer_seria(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    logging.info(f"{call.from_user.id} {call.message.from_user.full_name} {call.data}")
    await state.update_data({"passport_seria": call.data})
    await call.message.delete()
    await call.message.answer(f"Passportingiz raqamini kiriting: {call.data}", reply_markup=number_keyboard)
    await Learning.next()


@dp.callback_query_handler(lambda call: call.data in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "number_back"],
                           state=Learning.two)
@handle_errors
async def answer_passport_number(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    data = await state.get_data()
    passport_number = data.get("passport_number", "")
    logging.info(f"{call.from_user.id} {data.get('Name')} {call.data} {passport_number}")

    if call.data == "number_back" and passport_number:
        passport_number = passport_number[:-1]
    elif call.data != "number_back":
        passport_number += call.data

    await state.update_data({"passport_number": passport_number})

    if len(passport_number) == 7:
        full_passport = f"{data.get('passport_seria')}{passport_number}"
        if get_user_info(passport=full_passport):
            await call.message.answer(
                "Bu passport seriyasi va raqami bilan avval ro'yxatdan o'tgan. Iltimos, qaytadan urinib ko'ring!",
                reply_markup=choose_visitor)
            await state.reset_state(with_data=True)
        else:
            await state.update_data({"passport": full_passport})
            await call.message.delete()

            data1 = (
                f"Quyidagi kiritgan ma'lumotlaringiz to'g'ri ekanligini tasdiqlaysizmi?\n"
                f"F. I. SH: {data.get('Name')}\n"
                f"Passport: <b>{full_passport}</b>\n"
                f"Viloyat: {data.get('region')}\n"
                f"Tuman: {data.get('tuman')}\n"
                f"Yo'nalish: <b>{faculty_file_map2.get(data.get('yonalish'))}</b> ✅"
            )
            await call.message.answer(text=data1, reply_markup=response_keyboard)
            await Learning.three.set()
    else:
        await call.message.edit_text(f"Passport raqamini kiriting: {data.get('passport_seria')} {passport_number}",
                                     reply_markup=number_keyboard)


@dp.callback_query_handler(lambda call: call.data in ["yes", "no"], state=Learning.three)
@handle_errors
async def check(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    await call.message.delete()
    data = await state.get_data()

    if call.data == "yes":
        await call.message.answer(
            "✅ Ma'lumotlaringiz muvaffaqiyatli qabul qilindi.\nTanlagan yo'nalishda o'qishingiz uchun ariza qolding!",
            reply_markup=choose_contract_)

        db.update_user(telegram_id=str(call.from_user.id), name=data.get("Name"), passport=data.get("passport"),
                       faculty=faculty_file_map2.get(data.get('yonalish')), viloyat=data.get("region"),
                       tuman=data.get("tuman"))
        await state.update_data({"ariza_uuid": uuid4()})
        await Learning.next()
    elif call.data == "no":
        await call.message.answer("❌ Ma'lumotlaringiz muvaffaqiyatli qabul qilinmadi. Iltimos qaytadan urinib ko'ring!",
                                  reply_markup=choose_visitor)
        await state.reset_state(with_data=True)


@dp.callback_query_handler(lambda call: call.data in ["qabul_yes", "inkor_no"], state=Learning.four)
@handle_errors
async def check_choose(call: types.CallbackQuery, state: FSMContext, raw_state: FSMContext):
    await call.message.delete()
    data = await state.get_data()

    if call.data == "qabul_yes":
        await call.message.answer("Yuborgan arizangiz ko'rib chiqilmoqda ✅")
        await func_qrcode(url=data.get("ariza_uuid"), name=data.get("Name"), status=False)

        await process_document(address=f"{data.get('region')} {data.get('tuman')}da",
                               name=data.get("Name"),
                               file_name=await get_file_database_path(name=faculty_file_map.get(data.get('yonalish'))))

        response = await call.message.answer_document(
            types.InputFile(await get_file_path(name=f"file_ariza/{data.get('Name')}.pdf")),
            caption="Sizning arizangiz"
        )
        await dp.bot.send_message(ADMIN_M1,
                                  f"Arizachi:{data.get('Name')}\nPassport:<b>{data.get('passport')}</b>\nViloyat:{data.get('region')}\nTuman:{data.get('tuman')}\nYo'nalish:<b>{faculty_file_map2.get(data.get('yonalish'))}</b>",
                                  reply_markup=await keyboard_func(user_id=call.from_user.id, message=call.message,
                                                                   faculty=data.get('yonalish')))
        db.update_(telegram_id=str(call.from_user.id), updated_fields={"telegram_ariza_id": response.document.file_id})
        await state.reset_state(with_data=True)
    elif call.data == "inkor_no":
        await call.message.answer("❌ Arizangiz rad etildi. Iltimos qaytadan urinib ko'ring!")
        await exit_system(call.message, state)
