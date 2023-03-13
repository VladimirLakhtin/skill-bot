from aiogram.utils.exceptions import MessageNotModified

import random

from create_bot import dp
import data_checking
import keyboards.admin as keyboard
from state import FSMAddRecord, FSMContext
from func_bot import *
from filters import IsAdmin
from script_text.admin import text


# Add menu
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["add", "back_menu"], state="*")
async def add_menu(call, state: FSMContext):
    cur_text = random.choice(text["add"])
    await main_edit_mes(cur_text, ikb=keyboard.add_menu, call=call)
    if call.data != "add":
        await state.finish()


# Request name of record
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith('add_'))
async def request_name(call, state: FSMContext):
    table = call.data.split('_')[-1]
    if table == "students":
        rus_name, next_state = ['имя студента', FSMAddRecord.state_name]
    elif table == "teachers":
        rus_name, next_state = ['имя куратора', FSMAddRecord.state_name]
    elif table == "awards":
        rus_name, next_state = ['название награды', FSMAddRecord.state_title]
    else:
        rus_name, next_state = ['название задачи', FSMAddRecord.state_title]
    text = f"Введите <b>{rus_name}</b>"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
    async with state.proxy() as data:
        data["message_id_" + table] = call.message.message_id
        data["chat_id_" + table] = call.message.chat.id
        data["table"] = table
        data['count'] = 0
    await next_state.set()


# Request description of new award or task
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_title)
async def input_title(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        data["name_" + table] = message.text
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if table == "awards":
        mini_text = "Введите <b>описание</b> условий выполнения задания"
    else:
        mini_text = "Введите <b>описание</b> награды"
    await main_edit_mes(text=mini_text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.state_info_title.set()


# Request SkillCoins count for a task or award
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_info_title)
async def input_description(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        mini_text, data["description"] = ["Введите <b>кол-во Skillcoins</b>", message.text]
        await main_edit_mes(text=mini_text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await FSMAddRecord.state_cost.set()


# Check input cost and show all info about new task or award
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_cost)
async def input_cost(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        name_title = data["name_" + table]
        info = data["description"]
        data['count'] += 1
        rus_name_title = "награду" if table == "awards" else "выполненое задание"
        next_state = FSMAddRecord.state_cost
        flag, err_text = data_checking.input_edit(inputs=message.text, column='cost')
        if flag:
            text = f"Информация о введённых данных:" \
                   f"\nНазвание {name_title}" \
                   f"\nКол-во за {rus_name_title}: {message.text}" \
                   f"\nОписание: {info}"
            ikb = keyboard.accept_and_reject
            data["cost_" + table] = message.text
            next_state = FSMAddRecord.accept_or_reject
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
        elif data['count'] == 1:
            ikb = keyboard.back_add_menu
            await main_edit_mes(text=err_text, ikb=ikb, message_id=message_id, chat_id=chat_id)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await next_state.set()


# Request direction of student or teacher
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_name)
async def request_prof(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        if table == "students":
            mini_text = 'профессию студента'
            status = data_checking.cheak_input_text(message.text, key="имени")
            data["name_" + table] = status[-1]
        elif table == "teachers":
            mini_text = 'направление куратора'
            status = data_checking.cheak_input_text(message.text, key="имени")
            data["name_" + table] = status[-1]
        flag, text = data_checking.input_edit(message.text, column="name")
    if not flag:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        try:
            await main_edit_mes(text=text, message_id=message_id, chat_id=chat_id, ikb=keyboard.back_add_menu)
        except MessageNotModified:
            pass
        await FSMAddRecord.state_name.set()
    else:
        directions_id, directions_names = main_get(tables=['teachers'], columns=['id', 'direction'])
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        if status[1] == "ok":
            if table == 'students':
                ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option="add")
                text = f"Хорошо, теперь выбери <b>{mini_text}</b>"
                await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
            elif table == 'teachers':
                await main_edit_mes(f"Введите <b>название направления</b> куратора", ikb=keyboard.back_add_menu,
                                    message_id=message_id, chat_id=chat_id)
                async with state.proxy() as data:
                    data["call_message_id_teachers"] = message_id
                    data["call_chat_id_teachers"] = chat_id
            await FSMAddRecord.state_prof.set()
        elif status[1] == "normal":
            await main_edit_mes(text=status[0], ikb=keyboard.yes_and_no, message_id=message_id, chat_id=chat_id)
            await FSMAddRecord.next()
        else:
            await main_edit_mes(text=status[0], ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
            await FSMAddRecord.next()


# Input proccesing (fignya)
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["yes", "no"],
                           state=FSMAddRecord.state_yes_and_no)
async def input_processing(call, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        directions_id, directions_names = main_get(tables=['teachers'], columns=['id', 'direction'])
        ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option="add")
    rus_name = 'студента' if table == 'students' else 'куратора'
    if call.data == "yes":
        if table == 'students':
            text = f"Хорошо, теперь выберите <b>профессию {rus_name}</b>"
            await main_edit_mes(text=text, ikb=ikb, call=call)
            await FSMAddRecord.next()
        else:
            text = f"Введите название <b>направления куратора</b>"
            await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
            async with state.proxy() as data:
                data["call_message_id_teachers"] = call.message.message_id
                data["call_chat_id_teachers"] = call.message.chat.id
            await FSMAddRecord.state_prof.set()
    else:
        text = f"Введите <b>имя {rus_name}</b>"
        await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
        await FSMAddRecord.state_name.set()


# Request tg-name for new teacher
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_prof)
async def request_tg_id_tch(message, state: FSMContext):
    async with state.proxy() as data:
        message_id = data["call_message_id_teachers"]
        chat_id = data["call_chat_id_teachers"]
        data["prof"] = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    text = f"Теперь введите <b>Telegram-ник</b> куратора"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.state_tg_name.set()


# Request tg-name for new student
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith('prof'), state=FSMAddRecord.state_prof)
async def request_tg_id_std(call, state: FSMContext):
    text = f"Теперь введите <b>Telegram-ник</b> студента"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
    async with state.proxy() as data:
        data['prof'] = call.data.split('_')[-1]
        data["call_message_id_students"] = call.message.message_id
        data["call_chat_id_students"] = call.message.chat.id
    await FSMAddRecord.next()


# Show list with new record info
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_tg_name)
async def list_adding_info(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    rus_name = 'Студента' if table == 'students' else 'Куратора'
    async with state.proxy() as data:
        name = data["name_" + table]
        if table == 'students':
            teacher_name, direction = main_get(tables=['teachers'], columns=["name", 'direction'],
                                               condition=f"id = {data['prof']}", is_one=True)
            text = f"<b>Информация о введённых данных</b>\n\n" \
                   f"<b>{rus_name}</b> - {name}\n" \
                   f"<b>Группа</b> - {direction}\n" \
                   f"<b>Куратор</b> - {teacher_name}\n" \
                   f"<b>Telegram-ник</b> - {message.text}"
        else:
            direction = data["prof"]
            text = f"<b>Информация о введённых данных</b>\n\n" \
                   f"<b>{rus_name}</b> - {name}\n" \
                   f"<b>Направление</b> - {direction}\n" \
                   f"<b>Telegram-ник</b> - {message.text}"
        data["tg_username_" + table] = message.text[1:] if '@' in message.text[0] else message.text
        message_id_call = data["call_message_id_" + table]
        chat_id_call = data["call_chat_id_" + table]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await main_edit_mes(text=text, ikb=keyboard.accept_and_reject, message_id=message_id_call, chat_id=chat_id_call)
    await FSMAddRecord.accept_or_reject.set()


# Accept or reject add
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["accept", "reject"],
                           state=FSMAddRecord.accept_or_reject)
async def add_or_back_menu(call, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        name = data["name_" + table]
        try:
            tg_name = data["tg_username_" + table]
        except Exception:
            pass
    if call.data == "accept":
        if table == 'students':
            rus_name = 'Студент'
            direction = data['prof']
            params = {"name": f"'{name}'", "score": 0, "teacher_id": direction, 'tg_username': f"'{tg_name}'"}
        elif table == "teachers":
            rus_name = "Куратор"
            direction = data["prof"]
            params = {"name": f"'{name}'", "direction": f"'{direction}'", 'tg_username': f"'{tg_name}'"}
        elif table == "awards":
            rus_name = "Награда"
            description = data["description"]
            params = {"title": f"'{name}'", "cost": data["cost_" + table], 'description': f"'{description}'"}
            name = data["name_" + table] + data["cost_" + table]
        else:
            rus_name = "Задача"
            description = data["description"]
            params = {"title": f"'{name}'", "reward": data["cost_" + table], 'description': f"'{description}'"}
            name = data["name_" + table] + data["cost_" + table]
        add_record(table=table, params=params)
        await call.answer(f"Добавлена запись {rus_name}: {name}")
    cur_text = random.choice(text["add"])
    await main_edit_mes(text=cur_text, ikb=keyboard.add_menu, call=call)
    await state.finish()
