from aiogram.utils.exceptions import MessageNotModified

import data_checking
import keyboards.teacher as keyboard
from state import FSMContext, FSMEditFeat, FSMSeachRecord
from func_bot import *
from filters import IsTeacher
from create_bot import dp
from script_text.teacher import text
import random


# Search records
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data.startswith('edit'))
async def search_student(call, state: FSMContext):
    ikb = keyboard.create_ikb_records_list()
    text = f"Введите имя или фамилию студента которого хотите найти"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await call.answer("Поисковая система включена")
    await FSMSeachRecord.search_name_state.set()


# Show of search results
@dp.message_handler(IsTeacher(), state=FSMSeachRecord.search_name_state)
async def search_info_list_student(message, state: FSMContext):
    async with state.proxy() as data:
        message_id = data["message_search_id"]
        chat_id = data["chat_search_id"]
    teacher_id = main_get(tables=['teachers'], columns=['id'], condition=f'tg_id = {message.from_user.id}', is_one=True)
    records_id, records_name = get_search_results(table='students', name=message.text, teacher_id=teacher_id)
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if records_id:
        text = f"Студенты по запросу:"
        ikb = keyboard.create_ikb_records_list(records_id, records_name)
        await state.finish()
    else:
        text = "Сходства не найдены, попробуй еще раз или выведи всех:"
        ikb = keyboard.create_ikb_records_list()
        await FSMSeachRecord.search_name_state.set()
    try:
        await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
    except MessageNotModified:
        pass


# List of all records to edit
@dp.callback_query_handler(IsTeacher(), text='all', state="*")
async def edit_all_records_list(call, state: FSMContext):
    teacher_id = main_get(tables=['teachers'], columns=['id'], condition=f'tg_id = {call.from_user.id}', is_one=True)
    record_id, records_names = main_get(tables=['students'], columns=['id', 'name'],
                                        condition=f'teacher_id = {teacher_id}')
    ikb = keyboard.create_ikb_records_list(record_id, records_names, is_all=True)
    text = f"Все твои студенты SkillBox"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()


# Show full info about record
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data.startswith('std'), state="*")
async def edit_record_info(call, state: FSMContext):
    rec_id = call.data.split('_')[-1]
    text, columns = get_info_list(rec_id, table='students')
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["id"] = rec_id


# Request a new feature value
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data.startswith("feat_"))
async def edit_record_feat(call, state: FSMContext):
    _, rec_id, feat_name, feat_name_rus = call.data.split("_")
    ikb = keyboard.create_ikb_back_rec_info(rec_id)
    text = f"Введите изменение значении {feat_name_rus}"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["edit_call_message_id"] = call.message.message_id
        data["edit_call_chat_id"] = call.message.chat.id
        data["params"] = [rec_id, feat_name.replace("-", "_"), feat_name_rus]
    await FSMEditFeat.edit_records_state.set()


# Request confirm with changes
@dp.message_handler(IsTeacher(), state=FSMEditFeat.edit_records_state)
async def edit_record(message, state: FSMContext):
    async with state.proxy() as data:
        rec_id, feat_name, feat_name_rus = data["params"]
        message_id = data["edit_call_message_id"]
        chat_id = data["edit_call_chat_id"]
        data["answer"] = message.text
    flag, text = data_checking.input_edit(message.text, column=feat_name)
    if not flag:
        ikb = keyboard.create_ikb_back_rec_info(rec_id)
        try:
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
        except MessageNotModified:
            pass
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    else:
        cur_value = main_get(tables=['students'], columns=[feat_name], condition=f"id = {rec_id}", is_one=True)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        text = f"Вы точно хотите изменить {cur_value} на {message.text}"
        await main_edit_mes(text=text, ikb=keyboard.accept_and_reject_edit(), message_id=message_id, chat_id=chat_id)


# Accept or reject changes
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data in ["accept_edit", "reject_edit"],
                           state=FSMEditFeat.edit_records_state)
async def reject_or_accept_edit(call, state: FSMContext):
    async with state.proxy() as data:
        rec_id, feat_name, feat_name_rus = data["params"]
        answer = data["answer"]
    if call.data == "accept_edit":
        update_record('students', rec_id, {feat_name: answer})
    text, columns = get_info_list(rec_id, table='students')
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data['id'] = rec_id
    await call.answer("Изменил")
