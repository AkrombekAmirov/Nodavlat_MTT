from keyboards.inline import keyboard, yonalish_nomi_keyboard, response_keyboard, uzbekistan_viloyatlar, choose_visitor, \
    choose_contract_, seria_keyboard, number_keyboard, list_regioin, list_tuman, list_region1, response_admin, \
    keyboard_func
from file_service.file_read import process_document, process_contract, func_qrcode, write_qabul
from keyboards.inline.Dictionary import faculty_file_map, faculty_file_map2
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


@dp.message_handler(commands=['start'])
async def exit_system(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=True)  # Holatni tozalash
    await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def test(message: types.Message, state: FSMContext):
    print(message.from_user.username)
    db.add_user(telegram_id=str(message.from_user.id),
                username=str(message.from_user.username) if message.from_user.username else "",
                telegram_name=str(message.from_user.full_name),
                telegram_number=str(message.contact.phone_number))
    await message.answer("Xizmat turini tanlang", reply_markup=choose_visitor)


@dp.callback_query_handler(text="registration")
async def registration(call: types.CallbackQuery):
    await call.message.answer("Malaka oshirish kurslari yo'nalishini tanlang.", reply_markup=yonalish_nomi_keyboard)


@dp.callback_query_handler(
    lambda call: call.data in ["faculty0", "faculty1", "faculty2", "faculty3", "faculty4", "faculty5", "faculty6",
                               "faculty7", "faculty8", "faculty9", "faculty10", "faculty11"])
async def faculty(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"yonalish": call.data})
    await call.message.answer("Viloyatingizni tanglang.", reply_markup=uzbekistan_viloyatlar)


@dp.callback_query_handler(lambda call: call.data in list_regioin)
async def region(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"region": list_region1[int(call.data[3:])]})
    await call.message.answer("Tumanlarni tanlang.", reply_markup=await inline_tumanlar(call.data))


@dp.callback_query_handler(lambda call: call.data in list_tuman)
async def region(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"tuman": call.data})
    await call.message.answer("Familiya, Ism va Sharifingizni kiriting.")
    await Learning.zero.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Learning.zero)
async def answer_name(message: types.Message, state: FSMContext):
    logging.info(f"{message.from_user.id} {message.from_user.full_name} {message.text}")
    await message.delete()
    if message.text.startswith("/start"):
        await exit_system(message, state)
    elif re.match(r"^[A-Za-z\s']+$", message.text):
        await state.update_data({"Name": message.text})
        await message.answer("Pasportingiz seria va raqamini kiriting!", reply_markup=seria_keyboard)
        await Learning.next()
    else:
        await message.answer(
            "Siz malumot kiritishda xatolikga yo'l quydingiz! Iltimos Familiya, Ism va Sharifingizni  lotin alifbosida kiriting.")
        await Learning.zero.set()


@dp.callback_query_handler(lambda call: call.data in ["AA", "AB", "AC", "AD", "AE", "KA"], state=Learning.one)
async def answer_seria(call: types.CallbackQuery, state: FSMContext):
    logging.info(f"{call.from_user.id} {call.message.from_user.full_name} {call.data}")
    await state.update_data({"passport_seria": call.data})
    await call.message.delete()
    await call.message.answer(f"Passportingiz  raqamini kiriting: {call.data}", reply_markup=number_keyboard)
    await Learning.next()


@dp.callback_query_handler(lambda call: call.data in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "number_back"],
                           state=Learning.two)
async def answer_seria(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    logging.info(f"{call.from_user.id} {call.message.from_user.full_name} {call.data} {data.get('passport_number')}")
    if str(call.data) == "number_back" and len(str(data.get("passport_number"))) != 0:
        await state.update_data({"passport_number": f"{data.get('passport_number')[:-1]}"})
    elif str(data.get("passport_number"))[0:4] == "None":
        await state.update_data({"passport_number": call.data})
    elif str(call.data) != "number_back":
        await state.update_data({"passport_number": f"{data.get('passport_number')}{call.data}"})
    data = await state.get_data()
    if len(str(data.get("passport_number"))) == 7:
        print(data.get("passport_seria"), data.get("passport_number"))
        if get_user_info(passport=f"{data.get('passport_seria')}{data.get('passport_number')}"):
            await call.message.answer(
                "Bu passport seriyasi va raqami bilan avval ro'yxatdan o'tgan. Iltimos qaytadan urinib ko'ring!",
                reply_markup=choose_visitor)
            await state.reset_state(with_data=True)
        else:
            await state.update_data({"passport": data.get("passport_seria") + data.get("passport_number")})
            await call.message.delete()
            print(data.get('yonalish'), data.get('yonalish')[7])
            # faculty_name = "864 soatlik" if data.get('yonalish') == "faculty0" else "576 soatlik"
            data = await state.get_data()
            data1 = (
                f"Quyidagi kiritgan ma'lumotlaringiz to'g'ri ekanligini tasdiqlaysizmi?\nF. I. SH: {data.get('Name')}\nPassport: <b>{data.get('passport')}</b>\nViloyat: {data.get('region')}\nTuman: "
                f"{data.get('tuman')}\nYonalish: <b>{faculty_file_map2.get(data.get('yonalish'))}</b> ✅")
            await call.message.answer(text=data1, reply_markup=response_keyboard)
            await Learning.three.set()
    else:
        await call.message.edit_text(
            f"Passport raqamini kiriting: {data.get('passport_seria')} {data.get('passport_number')}",
            reply_markup=number_keyboard)


@dp.callback_query_handler(lambda call: call.data in ["yes", "no"], state=Learning.three)
async def check(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == "yes":
        await call.message.answer(
            "✅ Ma'lumotlaringiz muvaffaqiyatli qabul qilindi.\nTanlagan yunalishda o'qishingiz uchun ariza qolding!",
            reply_markup=choose_contract_)
        db.update_user(telegram_id=str(call.from_user.id), name=data.get("Name"), passport=data.get("passport"),
                       faculty=faculty_file_map2.get(data.get('yonalish')), viloyat=data.get("region"), tuman=data.get("tuman"),)
        await state.update_data({"ariza_uuid": uuid4()})
        await Learning.next()
    elif call.data == "no":
        await call.message.answer("❌ Ma'lumotlaringiz muvaffaqiyatli qabul qilinmadi. Iltimos qaytadan urinib ko'ring!",
                                  reply_markup=choose_visitor)
        await state.reset_state(with_data=True)


@dp.callback_query_handler(text="qabul_yes", state=Learning.four)
async def check_choose(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(call.data)
    print(await get_file_path(name=faculty_file_map.get(data.get('yonalish'))))
    if call.data == "qabul_yes":
        await call.message.answer("✅ Yuborgan arizangiz ko'rib chiqilmoqda.", reply_markup=choose_contract_)
        await func_qrcode(url=data.get("ariza_uuid"), name=data.get("Name"), status=False)
        await process_document(address=f"{data.get('region')} {data.get('tuman')}da", name=data.get("Name"),
                               file_name=await get_file_database_path(name=faculty_file_map.get(data.get('yonalish'))))
        await dp.bot.send_message(ADMINS,
                                  f"Arizachi:{data.get('Name')}\nPassport:{data.get('passport')}\nViloyat:{data.get('region')}\nTuman:{data.get('tuman')}\nYo'nalish:{faculty_file_map2.get(data.get('yonalish'))}",
                                  reply_markup=await keyboard_func(user_id=call.from_user.id, message=call.message, faculty=data.get('yonalish')))
        await state.reset_state(with_data=True)
