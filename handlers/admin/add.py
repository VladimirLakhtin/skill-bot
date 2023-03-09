import random

import data_checking
import keyboards.admin as keyboard
from state import FSMAddRecord, FSMContext
from func_bot import *
from filters import IsAdmin
from text import text_admin


# Add menu
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["add", "back_menu"], state="*")
async def add_menu(call, state: FSMContext):
    text = random.choice(text_admin.text["add"])
    await main_edit_mes(text=text, ikb=keyboard.add_menu, call=call)
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
        rus_name, next_state = ['название задачи для студентов', FSMAddRecord.state_title]
    text = f"Введите {rus_name}"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
    async with state.proxy() as data:
        data["message_id_" + table] = call.message.message_id
        data["chat_id_" + table] = call.message.chat.id
        data["table"] = table
        data['count'] = 0
    await next_state.set()


# Request SkillCoins count for a task or award
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_title)
async def input_title(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        data["name_" + table] = message.text
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    mini_text = "Введите кол-во Skillcoins для награды" if table == "awards" else "Введите кол-во Skillcoins за выполненое задание"
    await main_edit_mes(text=mini_text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.state_cost.set()


# Check input cost and show all info about new task or award
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_cost)
async def input_cost(message, state: FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        name_title = data["name_" + table]
        data['count'] += 1
        rus_name_title = "награду" if table == "awards" else "выполненое задание"
        next_state = FSMAddRecord.state_cost
        if data_checking.input_edit(inputs=message.text, column='cost'):
            text = f"Информация о введённых данных:\nНазвание {name_title}\nКол-во за {rus_name_title}: {message.text}"
            ikb = keyboard.accept_and_reject
            data["cost_" + table] = message.text
            next_state = FSMAddRecord.accept_or_reject
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
        elif data['count'] == 1:
            text = f"Введите положительное число"
            ikb = keyboard.back_add_menu
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
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
            mini_text = 'направления куратора'
            status = data_checking.cheak_input_text(message.text, key="имени")
            data["name_" + table] = status[-1]
        flag, text = data_checking.input_edit(message.text, column="name")
    if not flag:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        try:
            await main_edit_mes(text=text, message_id=message_id, chat_id=chat_id, ikb=keyboard.back_add_menu)
        except:
            pass
        await FSMAddRecord.state_name.set()
    else:
        directions_id, directions_names = main_get(tables=['teachers'], columns=['id', 'direction'])
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        if status[1] == "ok":
            if table == 'students':
                ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option="add")
                text = f"Хорошо, теперь выбери {mini_text}"
                await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
            elif table == 'teachers':
                await bot.edit_message_text(text=f"Введите названия направления куратора", message_id=message_id,
                                            chat_id=chat_id, reply_markup=keyboard.back_add_menu)
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
            text = f"Хорошо, теперь выбери профессию {rus_name}"
            await main_edit_mes(text=text, ikb=ikb, call=call)
            await FSMAddRecord.next()
        else:
            text = f"Введите названия направления куратора"
            await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
            async with state.proxy() as data:
                data["call_message_id_teachers"] = call.message.message_id
                data["call_chat_id_teachers"] = call.message.chat.id
            await FSMAddRecord.state_prof.set()
    else:
        text = f"Введите имя {rus_name}"
        await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
        await FSMAddRecord.state_name.set()


# Request tg-id for new teacher
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMAddRecord.state_prof)
async def request_tg_id_tch(message, state: FSMContext):
    async with state.proxy() as data:
        message_id = data["call_message_id_teachers"]
        chat_id = data["call_chat_id_teachers"]
        data["prof"] = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    text = f"Теперь введи ТГ name куратора"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.state_tg_name.set()


# Request tg-id for new student
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data.startswith('prof'), state=FSMAddRecord.state_prof)
async def request_tg_id_std(call, state: FSMContext):
    text = f"Теперь введи ТГ name студента"
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
            text = f"Информация о введённых данных\n\n{rus_name} - {name}\nГруппа - {direction}\nКуратор - {teacher_name}\nТГ ник - {message.text}"
        else:
            direction = data["prof"]
            teacher_name = ""
            text = f"Информация о введённых данных\n\n{rus_name} - {name}\n Направление - {direction}\nТГ ник - {message.text}"
        data["tg_username_" + table] = message.text
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
        tg_name = data["tg_username_" + table]
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
            params = {"title": f"'{name}'", "cost": data["cost_" + table]}
            name = data["name_" + table] + data["cost_" + table]
        else:
            rus_name = "Задача"
            params = {"title": f"'{name}'", "reward": data["cost_" + table]}
            name = data["name_" + table] + data["cost_" + table]
        add_record(table=table, params=params)
        await call.answer(f"{rus_name} {name} успешно добавлен\nХотите ещё что-то добавить?")
    text = random.choice(text_admin.text["add"])
    await main_edit_mes(text=text, ikb=keyboard.add_menu, call=call)
    await state.finish()
