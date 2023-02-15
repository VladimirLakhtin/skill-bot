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
@dp.callback_query_handler(lambda callback: callback.data == "back_menu_edit")
async def back_edit_menu(call, state:FSMContext):
    await state.finish()
    await bot.edit_message_text(text="Кого хотите отредактировать?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher)


#Редактирование и получения списка студентов или кураторов
@dp.callback_query_handler(lambda callback: callback.data in ["student_2", "teacher_2"])
async def edit_handler_student_teacher(call, state:FSMContext):
    my_key, rus_name, flag, prefix = ['student', 'студенты', True, 'std'] if call.data == 'student_2' else ['teacher', 'учителя', False, 'tch']
    records = func_bot.name_list_db_student_and_teacher(key=my_key)[0]
    ikb = keyboard.create_ikb(records, prefix)
    await bot.edit_message_text(
        text=f"Все {rus_name} SkillBox",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)
    async with state.proxy() as data:
        data["key_student_call"] = flag


#TODO: объединить
#Общая информация о студенте и действия удалить или назад
@dp.callback_query_handler(lambda callback: callback.data.startswith('std'))
async def edit_handler_message_student(call, state:FSMContext):
    async with state.proxy() as data:
        key = data["key_student_call"]
    if key:
        await bot.edit_message_text(
            text=func_bot.info_list(call.data[-1],key="student")[0],
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            reply_markup=keyboard.butt_back_and_del_prod)
        async with state.proxy() as data:
            data["id_student"] = func_bot.info_list(call.data[-1],key="student")[1]

            
#Общая информация о кураторе и действия удалить или назад
@dp.callback_query_handler(lambda callback: callback.data.startswith('tch'))
async def edit_handler_message_teacher(call, state: FSMContext):
    await bot.edit_message_text(
        text=func_bot.info_list(call.data[-1], key="teacher")[0],
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.butt_back_and_del_prod)
    async with state.proxy() as data:
        data["id_teacher"] = func_bot.info_list(call.data[-1], key="teacher")[1]

#Удаление куратора или студента из бд
@dp.callback_query_handler(lambda callback: callback.data in ["back", "del"])
async def back_and_del_student_handler(call, state:FSMContext):
    async with state.proxy() as data:
        key = data["key_student_call"]
    name, rus_name, prefix = ['student', 'студенты', 'std'] if key else ['teacher', 'кураторы', 'tch']
    if call.data == "del":
        async with state.proxy() as data:
            id_student = data['id_' + name]
        func_bot.removing_student(id_student)
    records = func_bot.name_list_db_student_and_teacher(key=name)[0]
    ikb = keyboard.create_ikb(records, prefix)
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
        chat_id=call.message.chat.id)
    async with state.proxy() as data:
        data["key_student_search"] = key_student_search
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await FSMAdmin.search_name_state.set()

#Принимаем данные message_text и обрабатываем функцию с вероятностью получая клавиатуру студентов или кураторов которые нашлись
@dp.callback_query_handler(lambda message: message.text, state=FSMAdmin.search_name_state)
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
@dp.callback_query_handler(lambda callback: callback.data in ["add", "back_menu"])
async def add_handler(call, state:FSMContext):
    await bot.edit_message_text(text="*Инструкция по добавлению*", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
    if call.data != "add":
        await state.finish()


#Добавление типов профессии
@dp.callback_query_handler(lambda callback: callback.data == "type")
async def add_type_handler(call, state:FSMContext):
    async with state.proxy() as data:
        data["message_id_type"] = call.message.message_id
        data["chat_id_type"] = call.message.chat.id
    await bot.edit_message_text(text=f"Введите название типа профессии", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
    await FSMAdmin.state_add_type_profession.set()


@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_add_type_profession)
async def add_name_type_handler(message, state:FSMContext):
    async with state.proxy() as data:
        data["type_name"] = message.text
        message_id = data["message_id_type"]
        chat_id = data["chat_id_type"]
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await bot.edit_message_text(text=f"Вы уверены что хотите добавить тип профессии - {message.text}", message_id=message_id, chat_id=chat_id, reply_markup=keyboard.accept_and_reject_2)
        await FSMAdmin.next()


@dp.callback_query_handler(lambda callback: callback.data in ["accept_2", "reject_2"])
async def accept_or_reject_type_handler(call, state:FSMContext):
    if call.data == "accept_2":
        async with state.proxy() as data:
            type_name = data["type_name"]
            func_bot.add_type(type_name)
        await bot.edit_message_text(text=f"Тип профессии - {type_name} успешно добавлен\n\nЧто ещё хотите добавить?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
    else:
        await bot.edit_message_text(text=f"Хорошо\nЧто то хотите добавить?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
    await state.finish()


#Добавление
@dp.callback_query_handler(lambda callback: callback.data in ["student", "teacher"])
async def add_studenta_or_teacher_handler(call, state:FSMContext):
    postfix, flag, rus_name = ['std', True, 'студента'] if call.data == "student" else ['tch', False, 'куратора']
    await bot.edit_message_text(text=f"Введите имя {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
    async with state.proxy() as data:
        data["message_id_" + postfix] = call.message.message_id
        data["chat_id_" + postfix] = call.message.chat.id
        data["student"] = flag
    await FSMAdmin.state_add_name.set()


@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_add_name)
async def add_name_student_or_teacher_handler(message, state:FSMContext):
    async with state.proxy() as data:
        key_student = data["student"]
        list_type = [i[1] for i in func_bot.db("Type_and_articul")]
        ikb = keyboard.create_ikb(list_type, 'type')
        status = data_checking.cheak_input_text(message.text, key="имени")
    postfix, mini_text = ['std', 'профессию студента'] if key_student else ['tch', 'направления куратора']
    async with state.proxy() as data:
        data["name_" + postfix] = status[-1]
        chat_id = data["chat_id_" + postfix]
        message_id = data["message_id_" + postfix]
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if status[1] == "ok":
        await bot.edit_message_text(text=f"Хорошо, теперь выбери {mini_text}", message_id=message_id, chat_id=chat_id, reply_markup=ikb)
        await FSMAdmin.next()
        await FSMAdmin.next()
    elif status[1] == "normal":
        await bot.edit_message_text(text=status[0], message_id=message_id, chat_id=chat_id, reply_markup=keyboard.yes_and_no)
        await FSMAdmin.next()
    else:
        await bot.edit_message_text(text=status[0], message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_inline_menu_butt)
        await FSMAdmin.state_add_name.set()


@dp.callback_query_handler(lambda callback: callback.data in ["yes", "no"], state=FSMAdmin.state_yes_and_no)
async def yes_and_no_handler(call, state:FSMContext):
    async with state.proxy() as data:
        key_student = data["student"]
        list_type = [i[1] for i in func_bot.db("Type_and_articul")]
        ikb = keyboard.create_ikb(list_type, 'type')
    rus_name = 'студента' if key_student else 'куратора'
    if call.data == "yes":
        await bot.edit_message_text(text=f"Хорошо, теперь выбери профессию {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=ikb)
        await FSMAdmin.next()
    else:
        await bot.edit_message_text(text=f"Введите имя {rus_name}", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
        await FSMAdmin.state_add_name.set()


@dp.callback_query_handler(lambda callback: callback.data.startswith('type'), state=FSMAdmin.state_add_type)
async def add_type_student_or_teacher_handler(call, state:FSMContext):
    async with state.proxy() as data:
        key_student = data["student"]
    postfix, rus_name = ['std', 'студента'] if key_student else ['tch', 'куратора']

    await bot.edit_message_text(text=f"Теперь введи ТГ id {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_inline_menu_butt)
    async with state.proxy() as data:
        data["type_" + postfix] = func_bot.db("Type_and_articul")[int(call.data[-1]) - 1][1]
        data["articul_" + postfix] = func_bot.db("Type_and_articul")[int(call.data[-1]) - 1][0]
        data["call_message_id_" + postfix] = call.message.message_id
        data["call_chat_id_" + postfix] = call.message.chat.id
    await FSMAdmin.next()


@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_add_tg_name)
async def add_tg_name_student_or_teacher_handler(message, state:FSMContext):
    async with state.proxy() as data:
        key_student = data["student"]
    postfix, rus_name = ['std', 'Студент'] if key_student else ['tch', 'Куратор']
    async with state.proxy() as data:
        name = data["name_" + postfix]
        prof = data["type_" + postfix]
        articul = data["articul_" + postfix]
        data["tg_id_" + postfix] = message.text
        message_id_call = data["call_message_id_" + postfix]
        chat_id_call = data["call_chat_id_" + postfix]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.edit_message_text(text=f"Информация о введённых данных\n\n {rus_name} - {name}\n\nГруппа - {prof}\nАртикул группы - {articul}\nТГ ник - {message.text}", chat_id=chat_id_call, message_id=message_id_call, reply_markup=keyboard.accept_and_reject)
    await FSMAdmin.next()


@dp.callback_query_handler(lambda callback: callback.data in ["accept", "reject"] or callback.data in ["accept_2", "reject_2"], state=FSMAdmin.accept_or_reject)
async def accept_or_reject_add_student_or_teacher_handler(call, state:FSMContext):
    async with state.proxy() as data:
        key_student = data["student"]
    postfix, rus_name = ['std', 'Студент'] if key_student else ['tch', 'Куратор']
    if call.data == "accept":
        async with state.proxy() as data:
            name = data["name_" + postfix]
            prof = data["type_" + postfix]
            articul = data["articul_" + postfix]
            tg_id = data["tg_id_" + postfix]
            func_bot.add_student(name=name, type=prof, articul=articul, id_tg=tg_id, class_human=rus_name)
            await bot.edit_message_text(text=f"{rus_name} {name} успешно добавлен\nХотите ещё что-то добавить?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
            await state.finish()
    else:
        await bot.edit_message_text(text="*Инструкция по добавлению*", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.student_and_teacher_type)
    await state.finish()
