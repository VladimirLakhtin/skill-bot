import data_checking
import keyboards.teacher as keyboard
from state import FSMAddRecord, FSMContext
from func_bot import *
from filters import IsTeacher
from script_text.teacher import text
from create_bot import dp
from datetime import date
import random


# Request name of student
@dp.callback_query_handler(IsTeacher(), text='add_std')
async def request_name(call, state: FSMContext):
    text = f"Введите <b>имя и фамилию</b>"
    await main_edit_mes(text=text, ikb=keyboard.back_main_menu, call=call)
    async with state.proxy() as data:
        data["message_id"] = call.message.message_id
        data["chat_id"] = call.message.chat.id
    await FSMAddRecord.state_name.set()


# Request tg-name for new student
@dp.message_handler(IsTeacher(), state=FSMAddRecord.state_name)
async def request_tg_id_std(message, state: FSMContext):
    flag, text = data_checking.input_edit(message.text, column="name")
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    async with state.proxy() as data:
        data["name"] = message.text
        message_id = data["message_id"]
        chat_id = data["chat_id"]
    if not flag:
        try:
            await main_edit_mes(text=text, message_id=message_id, chat_id=chat_id, ikb=keyboard.back_main_menu)
        except:
            pass
        await FSMAddRecord.state_name.set()
    else:
        text = f"Теперь введите <b>Telegram-ник</b> студента"
        await main_edit_mes(text=text, ikb=keyboard.back_main_menu, message_id=message_id, chat_id=chat_id)
        await FSMAddRecord.state_tg_name.set()


# Show list with new record info
@dp.message_handler(IsTeacher(), lambda message: message.text, state=FSMAddRecord.state_tg_name)
async def list_adding_info(message, state: FSMContext):
    async with state.proxy() as data:
        name = data["name"]
        teacher_id, teacher_name, direction = main_get(tables=['teachers'], columns=["id", "name", 'direction'],
                                                       condition=f"tg_id = {message.from_user.id}", is_one=True)
        text = f"<b>Информация о введённых данных</b>\n\n" \
               f"<b>ФИ студента</b> - {name}\n" \
               f"<b>Направление</b> - {direction}\n" \
               f"<b>Куратор</b> - {teacher_name}\n" \
               f"<b>Telegram-ник</b> - {message.text}"
        data["teacher_id"] = teacher_id
        data["direction"] = direction
        data["tg_username"] = message.text[1:] if '@' in message.text[0] else message.text
        message_id = data['message_id']
        chat_id = data["chat_id"]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await main_edit_mes(text=text, ikb=keyboard.accept_or_reject, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.accept_or_reject.set()


# Accept or reject adding / Back to main menu
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data in ["accept", "reject"],
                           state=FSMAddRecord.accept_or_reject)
async def add_or_back_menu(call, state: FSMContext):
    async with state.proxy() as data:
        name = data["name"]
        tg_name = data["tg_username"]
    if call.data == "accept":
        teacher_id = data['teacher_id']
        params = {"name": f"'{name}'", "score": 0, "teacher_id": f"'{teacher_id}'", 'tg_username': f"'{tg_name}'"}
        add_record(table='students', params=params)
        await call.answer(f"Студент {name} успешно добавлен")
    await main_edit_mes(text=text['start'], ikb=keyboard.kb_main, call=call)
    await state.finish()
