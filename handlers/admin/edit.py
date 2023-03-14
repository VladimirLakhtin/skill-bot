from aiogram.utils.exceptions import MessageNotModified

import random
from create_bot import dp
from state import FSMContext, FSMEditFeat, FSMSeachRecord
import data_checking
import keyboards.admin as keyboard
from func_bot import *
from filters import IsAdmin
from script_text.admin import text


# Edit menu
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data == "edit")
async def edit_menu(call):
    await main_edit_mes(random.choice(text["edit"]), ikb=keyboard.edit_menu, call=call)


# Back to edit menu / Delete record
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["back_menu_edit", "del"], state="*")
async def back_edit_menu(call, state: FSMContext):
    if call.data == "del":
        async with state.proxy() as data:
            table = data["table"]
            record_id = data['id_' + table]
        if table == "awards":
            rus_name = "награду"
            colum = "title"
        elif table == "students":
            rus_name = "студента"
            colum = "name"
        elif table == "teachers":
            rus_name = "куратора"
            colum = "name"
        else:
            rus_name = "задачу"
            colum = "title"
        name = main_get(tables=[table], columns=[colum], condition=f'id = {record_id}', is_one=True)
        await main_edit_mes(f"Вы точно хотите <b>удалить {rus_name} {name}</b>?", call=call, ikb=keyboard.yes_and_no_del)
    else:
        await main_edit_mes(text=random.choice(text['edit']), ikb=keyboard.edit_menu, call=call)
        await state.finish()


@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["yes_del", "no_del"], state="*")
async def del_record(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        record_id = data['id_' + table]
    if call.data == "yes_del":
        if table == "awards":
            rus_name = "награду"
            colum = "title"
        elif table == "students":
            rus_name = "студента"
            colum = "name"
        elif table == "teachers":
            rus_name = "куратора"
            colum = "name"
        else:
            rus_name = "задачу"
            colum = "title"
        name = main_get(tables=[table], columns=[colum], condition=f'id = {record_id}', is_one=True)
        remove_record(record_id=record_id, table=table)
        await call.answer(f'Запись {rus_name} {name} удалена')
        remove_record(record_id=record_id, table=table)

    await main_edit_mes(text=random.choice(text['edit']), ikb=keyboard.edit_menu, call=call)
    await state.finish()


# Get list of all tasks of awards to edit
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["awards_edit", "tasks_edit"])
async def get_title_list(call, state: FSMContext):
    table, text = ["awards", "Список всех наград 🥇"] if call.data == "awards_edit" else ["tasks", "Список всех задач 🧑🏻‍💻"]
    rec_id, records_name = main_get(tables=[table], columns=['id', 'title'], sort_by='title')
    ikb = keyboard.create_ikb_records_list(rec_id, records_name, type_class=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["table"] = table


# Get full info about a task or award
@dp.callback_query_handler(IsAdmin(),
                           lambda callback: callback.data.startswith("awards") or callback.data.startswith("tasks"),
                           state="*")
async def get_record_info_title(call, state: FSMContext):
    async with state.proxy() as data:
        if 'table' in data.keys():
            table = data["table"]
        else:
            _, _, table, _ = data["params"]
            data["table"] = table
    rec_id = call.data.split('_')[-1]
    text, columns = get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["id_" + table] = rec_id
        data["table"] = table


# List of all students or teachers to edit
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith('all_'), state="*")
async def edit_all_records_list(call, state: FSMContext):
    table, rus_name, prefix = ['students', 'студенты', 'std'] if call.data == 'all_std' else ['teachers', 'учителя', 'tch']
    step, cur_step = 10, 0
    record_id, records_names = main_get(tables=[table], columns=['id', 'name'], sort_by='name')
    ikb = keyboard.create_ikb_records_list(record_id, records_names, prefix, option="edit", step=step, cur_step=cur_step)
    text = f"Все {rus_name} SkillBox 1 страница"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["next_inline"] = [record_id, records_names, prefix, step, rus_name, cur_step]


# Get next or previous page of students list
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["next_inline", "back_inline"], state="*")
async def next_inline(call, state: FSMContext):
    async with state.proxy() as data:
        record_id, records_names, prefix, step, rus_name, cur_step = data["next_inline"]
    diff = 10 if call.data == "next_inline" else -10
    step += diff
    cur_step += diff
    ikb = keyboard.create_ikb_records_list(record_id, records_names, prefix, option="edit",
                                           step=step, cur_step=cur_step)
    text = f"Все {rus_name} SkillBox {round(step / 10)} страница"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["next_inline"] = [record_id, records_names, prefix, step, rus_name, cur_step]


# Show full info about a student or teacher
@dp.callback_query_handler(IsAdmin(),
                           lambda callback: callback.data.startswith('std') or callback.data.startswith('tch'),
                           state="*")
async def edit_record_info(call, state: FSMContext):
    table = 'students' if call.data.split('_')[0] == 'std' else 'teachers'
    rec_id = call.data.split('_')[-1]
    text, columns = get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data[f"id_{table}"] = rec_id
        data["table"] = table


# Request student or teacher name to make search
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith('edit'))
async def search_student_teacher_handler(call, state: FSMContext):
    table, rus_text = ['students', "студента"] if call.data == "edit_std" else ['teachers', "куратора"]
    ikb = keyboard.create_ikb_back_edit_menu(call.data.split('_')[-1])
    text = f"Введите <b>имя или фамилию {rus_text}</b> которого хотите найти 👀"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["table"] = table
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await call.answer("Поисковая система включена")
    await FSMSeachRecord.search_name_state.set()


# Show of search results
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMSeachRecord.search_name_state)
async def search_info_list_student_teacher(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        message_id = data["message_search_id"]
        chat_id = data["chat_search_id"]
    records_id, records_name = get_search_results(table=table, name=message.text)
    type_class, rus_text = ["std", "Студенты"] if table == 'students' else ["tch", "Кураторы"]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if records_id:
        text = f"{rus_text} по запросу:"
        ikb = keyboard.create_ikb_records_list(records_id, records_name, type_class, "search")
        await state.finish()
    else:
        text = "<b>Сходства не найдены</b>, попробуй еще раз или выведи всех: 🤷🏼‍♂️"
        ikb = keyboard.create_ikb_back_edit_menu(type_class)
        await FSMSeachRecord.search_name_state.set()
    try:
        await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
    except MessageNotModified:
        pass


# Request a new feature value
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith("feat_"))
async def edit_record_feat(call, state: FSMContext):
    _, rec_id, feat_name, feat_name_rus, table = call.data.split("_")
    if table == "students" and feat_name == "direction":
        directions_id, directions_names = main_get(tables=['teachers'], columns=['id', 'direction'])
        ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option='edit',
                                               std_id=rec_id)
    else:
        ikb = keyboard.create_ikb_back_rec_info(rec_id, table)
    text = f"Введите изменение значения <b>{feat_name_rus}</b>"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["edit_call_message_id"] = call.message.message_id
        data["edit_call_chat_id"] = call.message.chat.id
        data["params"] = [rec_id, feat_name.replace("-", "_"), table, feat_name_rus]
    await FSMEditFeat.edit_records_state.set()


# Request a new student direction value
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith("prof_"),
                           state=FSMEditFeat.edit_records_state)
async def edit_student_prof(call, state: FSMContext):
    rec_id_prof = call.data.split("_")[1]
    async with state.proxy() as data:
        rec_id_std = data["params"][0]
        new_value = main_get(tables=['teachers'], columns=['direction'], condition=f"id = {rec_id_prof}", is_one=True)
        cur_value = main_get(tables=["students", "teachers"], columns=['teachers.direction'],
                             condition=f"students.id = {rec_id_std}", is_one=True)
        data["answer"] = rec_id_prof
    text = f"Вы точно хотите изменить <b>{cur_value}</b> на <b>{new_value}</b>"
    await main_edit_mes(text=text, ikb=keyboard.accept_and_reject_edit, call=call)


# Request confirm with changes
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMEditFeat.edit_records_state)
async def edit_record(message, state: FSMContext):
    async with state.proxy() as data:
        params = data["params"]
        message_id = data["edit_call_message_id"]
        chat_id = data["edit_call_chat_id"]
        data["answer"] = message.text
        rec_id, feat_name, table, feat_name_rus = params
    flag, text = data_checking.input_edit(message.text, column=feat_name)
    if not flag:
        ikb = keyboard.create_ikb_back_rec_info(rec_id, table)
        try:
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
        except MessageNotModified:
            pass
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    else:
        cur_value = main_get(tables=[table], columns=[feat_name], condition=f"id = {rec_id}", is_one=True)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        text = f"Вы точно хотите изменить <b>{cur_value}</b> на <b>{message.text}</b>"
        await main_edit_mes(text=text, ikb=keyboard.accept_and_reject_edit, message_id=message_id, chat_id=chat_id)


# Accept or reject changes
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["accept_edit", "reject_edit"],
                           state=FSMEditFeat.edit_records_state)
async def reject_or_accept_edit(call, state: FSMContext):
    async with state.proxy() as data:
        params = data["params"]
        answer = data["answer"]
    rec_id, feat_name, table, _ = params
    feat_name = 'teacher_id' if feat_name == 'direction' and table == 'students' else feat_name
    if call.data == "accept_edit":
        update_record(table, rec_id, {feat_name: answer})
        await call.answer("Изменил")
    text, columns = get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data['table'] = table
        data['id_' + table] = rec_id