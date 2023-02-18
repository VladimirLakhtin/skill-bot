import data_checking
import keyboard
from create_bot import bot, dp
from state import FSMAdmin, FSMContext

import func_bot

#Главное меню админа
@dp.message_handler(commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню, {message.from_user.first_name}", reply_markup=keyboard.ka_main)

#Выход в главное меню админа
@dp.callback_query_handler(lambda callback: callback.data == "back_main_menu")
async def back_main_menu(call, state:FSMContext):
    await state.finish()
    await bot.edit_message_text(
        text=f"Добро пожаловать в главное мнею {call.message.from_user.first_name}",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.ka_main)


#Меню редавктирования
@dp.callback_query_handler(lambda callback: callback.data == "edit")
async def edit_handler(call):
    await bot.edit_message_text(text="Кого хотите отредактировать?", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher)


#Выход в меню редактирования
@dp.callback_query_handler(lambda callback: callback.data == "back_menu_edit", state="*")
async def back_edit_menu(call, state:FSMContext):
    await state.finish()
    await bot.edit_message_text(text="Кого хотите отредактировать?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher)


#Редактирование и получения списка студентов или кураторов
@dp.callback_query_handler(lambda callback: callback.data.startswith('edit'))
async def edit_handler_student_teacher(call):
    table, rus_name, prefix = ['students', 'студенты', 'std'] if call.data == 'edit_std' else ['teachers', 'учителя', 'tch']
    record_id, records_names = func_bot.main_get(tables=[table], columns=['id', 'name'])
    ikb = keyboard.create_ikb(record_id, records_names, prefix)
    await bot.edit_message_text(
        text=f"Все {rus_name} SkillBox",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)


#Общая информация о студенте и действия удалить или назад
@dp.callback_query_handler(lambda callback: callback.data.startswith('std') or callback.data.startswith('tch'))
async def edit_handler_message_student(call, state:FSMContext):
    table = 'students' if call.data.split('_')[0] == 'std' else 'teachers'
    record_id = call.data.split('_')[-1]
    await bot.edit_message_text(
        text=func_bot.get_info_list(record_id, table=table),
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.butt_back_and_del_prod)
    async with state.proxy() as data:
        data[f"id_{table}"] = record_id
        data["table"] = table


#Удаление куратора или студента из бд
@dp.callback_query_handler(lambda callback: callback.data in ["back", "del"])
async def back_and_del_student_handler(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    rus_name, prefix = ['студенты', 'std'] if table == 'students' else ['кураторы', 'tch']
    if call.data == "del":
        async with state.proxy() as data:
            record_id = data['id_' + table]
        func_bot.remove_record(record_id=record_id, table=table)
    record_id, records_names = func_bot.main_get(tables=[table], columns=['id', 'name'])
    ikb = keyboard.create_ikb(record_id, records_names, prefix)
    await bot.edit_message_text(
        text=f"Все {rus_name} SkillBox",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)


#Вход в меню поиска
@dp.callback_query_handler(lambda callback: callback.data == "search", state=None)
async def search_handler(call):
    await bot.edit_message_text(
        text=f"Кого ищем?",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.student_and_teacher_search)
    
#Ожидаем call данных от пользователя и добавляем ключ студента и входим в состояния
@dp.callback_query_handler(lambda callback: callback.data in ["teacher_search", "student_search"])
async def search_student_teacher_handler(call, state:FSMContext):
    key_student_search, rus_text = [True, "студента"] if call.data == "student_search" else [False, "куратора"]
    await bot.edit_message_text(
        text=f"Введите имя {rus_text} которого хотите найти",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.back_inline_menu_edit_butt)
    async with state.proxy() as data:
        data["key_student_search"] = key_student_search
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await FSMAdmin.search_name_state.set()

#Принимаем данные message_text и обрабатываем функцию с вероятностью получая клавиатуру студентов или кураторов которые нашлись
@dp.message_handler(lambda message: message.text, state=FSMAdmin.search_name_state)
async def search_info_list_student_teacher(message, state:FSMContext):
    async with state.proxy() as data:
        key_student_search = data["key_student_search"]
        message_id = data["message_search_id"]
        chat_id = data["chat_search_id"]
        if key_student_search:
            records = func_bot.search_db_student_teacher(key="student", name=message.text)
        else:
            records = func_bot.search_db_student_teacher(key="teacher", name=message.text)
        posfix, rus_text = ["schs", "студентов"] if key_student_search else ["scht", "кураторов"]
        ikb = keyboard.create_ikb(records, posfix)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await state.finish()
        await bot.edit_message_text(
            text=f"Все {rus_text} имена которые совпали с вашим запросом",
            message_id=message_id,
            chat_id=chat_id,
            reply_markup=ikb)
        async with state.proxy() as data:
            data["key_student_search"] = key_student_search

#Берём данные по нашедшему студенту нажав на кнопку
@dp.callback_query_handler(lambda callback: callback.data.startswith("schs"))
async def search_info_student(call, state:FSMContext):
    async with state.proxy() as data:
        key = data["key_student_search"]
    if key:
        await bot.edit_message_text(
            text=func_bot.info_list(call.data[-1], key="student")[0],
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            reply_markup=keyboard.butt_back_and_del_search)
        async with state.proxy() as data:
            data["id_student_search"] = func_bot.info_list(call.data[-1], key="student")[1]


#Берём данные по нашедшему куратору нажав на кнопку
@dp.callback_query_handler(lambda callback: callback.data.startswith("scht"))
async def search_info_teacher(call, state:FSMContext):
        await bot.edit_message_text(
            text=func_bot.info_list(call.data[-1], key="teacher")[0],
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            reply_markup=keyboard.butt_back_and_del_search)
        async with state.proxy() as data:
            data["id_teacher_search"] = func_bot.info_list(call.data[-1], key="teacher")[1]

#Удаляем студента или куратора или же выходим на главное меню
#TODO: Буду доробатывать хочу сделать просто откат на хендлере что бы мог искать сколько угодно а не один раз
@dp.callback_query_handler(lambda callback: callback.data in ["back_menu_edit", "del_search"])
async def del_search_student_teacher(call, state:FSMContext):
    async with state.proxy() as data:
        key = data["key_student_search"]
    name, rus_name, prefix = ['student', 'студенты', 'std'] if key else ['teacher', 'кураторы', 'tch']
    if call.data == "del_search":
        async with state.proxy() as data:
            id_student = data['id_' + name + "_search"]
        func_bot.removing_student(id_student)
    await bot.edit_message_text(text="Кого хотите отредактировать?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher)


#Всё устал писать я спать коменты)


#Добавление
@dp.callback_query_handler(lambda callback: callback.data in ["add", "back_menu"], state="*")
async def add_handler(call, state:FSMContext):
    await bot.edit_message_text(text="*Инструкция по добавлению*", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
    if call.data != "add":
        await state.finish()


#Добавление
@dp.callback_query_handler(lambda callback: callback.data.startswith('add_'))
async def add_studenta_or_teacher_handler(call, state:FSMContext):
    postfix = call.data.split('_')[-1]
    table, rus_name = ['students', 'студента'] if postfix == "std" else ['teachers', 'куратора']
    await bot.edit_message_text(text=f"Введите имя {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
    async with state.proxy() as data:
        data["message_id_" + postfix] = call.message.message_id
        data["chat_id_" + postfix] = call.message.chat.id
        data["table"] = table
    await FSMAdmin.state_add_name.set()


@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_add_name)
async def add_name_student_or_teacher_handler(message, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    postfix, mini_text = ['std', 'профессию студента'] if table == 'students' else ['tch', 'направления куратора']
    status = data_checking.cheak_input_text(message.text, key="имени")
    async with state.proxy() as data:
        data["name_" + postfix] = status[-1]
        chat_id = data["chat_id_" + postfix]
        message_id = data["message_id_" + postfix]
        directions_id, directions_names = func_bot.main_get(tables=['teachers'], columns=['id', 'direction'])
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)

    if status[1] == "ok":
        if table == 'students':
            ikb = keyboard.create_ikb(directions_id, directions_names, type_class='type')
            await bot.edit_message_text(text=f"Хорошо, теперь выбери {mini_text}", message_id=message_id, chat_id=chat_id, reply_markup=ikb)
            await FSMAdmin.next()
            await FSMAdmin.next()
        else:
            await bot.edit_message_text(text=f"Введите названия направления куратора", message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_inline_menu_butt)
            async with state.proxy() as data:
                data["call_message_id_tch"] = message_id
                data["call_chat_id_tch"] = chat_id
            await FSMAdmin.state_add_profession.set()
    elif status[1] == "normal":
        await bot.edit_message_text(text=status[0], message_id=message_id, chat_id=chat_id, reply_markup=keyboard.yes_and_no)
        await FSMAdmin.next()
    else:
        await bot.edit_message_text(text=status[0], message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_inline_menu_butt)
        await FSMAdmin.next()


@dp.callback_query_handler(lambda callback: callback.data in ["yes", "no"], state=FSMAdmin.state_yes_and_no)
async def yes_and_no_handler(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        directions_id, directions_names = func_bot.main_get(tables=['teachers'], columns=['id', 'direction'])
        ikb = keyboard.create_ikb(directions_id, directions_names, type_class='type')
    rus_name = 'студента' if table == 'students' else 'куратора'
    if call.data == "yes":
        if table == 'students':
            await bot.edit_message_text(text=f"Хорошо, теперь выбери профессию {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=ikb)
            await FSMAdmin.next()
        else:
            await bot.edit_message_text(text=f"Введите названия направления куратора", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
            async with state.proxy() as data:
                data["call_message_id_tch"] = call.message.message_id
                data["call_chat_id_tch"] = call.message.chat.id
            await FSMAdmin.state_add_profession.set()
    else:
        await bot.edit_message_text(text=f"Введите имя {rus_name}", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
        await FSMAdmin.state_add_name.set()


@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_add_profession)
async def add_prof_teacher(message, state:FSMContext):
    async with state.proxy() as data:
        message_id = data["call_message_id_tch"]
        chat_id = data["call_chat_id_tch"]
        data["prof"] = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.edit_message_text(text=f"Теперь введи ТГ id куратора", message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_inline_menu_butt)
    await FSMAdmin.state_add_tg_name.set()


@dp.callback_query_handler(lambda callback: callback.data.startswith('type'), state=FSMAdmin.state_add_type)
async def add_type_student_or_teacher_handler(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    postfix, rus_name = ['std', 'студента'] if table == 'students' else ['tch', 'куратора']

    await bot.edit_message_text(text=f"Теперь введи ТГ id {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
    async with state.proxy() as data:
        data["type_" + postfix] = call.data.split('_')[-1]
        data["call_message_id_" + postfix] = call.message.message_id
        data["call_chat_id_" + postfix] = call.message.chat.id
    await FSMAdmin.next()


@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_add_tg_name)
async def add_tg_name_student_or_teacher_handler(message, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    postfix, rus_name = ['std', 'Студента'] if table == 'students' else ['tch', 'Куратора']
    async with state.proxy() as data:
        name = data["name_" + postfix]
        if table == 'students':
            teacher_name, direction = func_bot.main_get(tables=['teachers'], columns=["name", 'direction'], condition=f"id = {data['type_' + postfix]}", is_one=True)
        else:
            direction = data["prof"]
            teacher_name = ""
        data["tg_id_" + postfix] = message.text
        message_id_call = data["call_message_id_" + postfix]
        chat_id_call = data["call_chat_id_" + postfix]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.edit_message_text(text=f"Информация о введённых данных\n\n{rus_name} - {name}\nГруппа - {direction}\nКуратор - {teacher_name}\nТГ ник - {message.text}", chat_id=chat_id_call, message_id=message_id_call, reply_markup=keyboard.accept_and_reject)
    await FSMAdmin.next()


@dp.callback_query_handler(lambda callback: callback.data in ["accept", "reject"] or callback.data in ["accept_2", "reject_2"], state=FSMAdmin.accept_or_reject)
async def accept_or_reject_add_student_or_teacher_handler(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    postfix, rus_name = ['std', 'Студент'] if table == 'students' else ['tch', 'Куратор']
    if call.data == "accept":
        async with state.proxy() as data:
            name = data["name_" + postfix]
            tg_id = data["tg_id_" + postfix]
            if table == 'students':
                direction = data["type_" + postfix]
                params = {"name": f"'{name}'", "score": 0, "teacher_id": direction, 'tg_id': tg_id}
            else:
                direction = data["prof"]
                params = {"name": f"'{name}'", "direction": direction, 'tg_id': tg_id}
                print(params)
        func_bot.add_record(table=table, params=params)
        await bot.edit_message_text(text=f"{rus_name} {name} успешно добавлен\nХотите ещё что-то добавить?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
        await state.finish()
    else:
        await bot.edit_message_text(text="*Инструкция по добавлению*", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
    await state.finish()

