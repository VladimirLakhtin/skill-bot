import data_checking
import keyboards.admin_keyboards as keyboard
import state
from create_bot import bot, dp
from state import FSMAdmin, FSMContext

import func_bot


#------------------------------------------------Main------------------------------------------------

# Main menu
@dp.message_handler(commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню, {message.from_user.first_name}", reply_markup=keyboard.kb_main)


# Back to main menu
@dp.callback_query_handler(lambda callback: callback.data == "back_main_menu")
async def back_main_menu(call, state:FSMContext):
    await state.finish()
    await bot.edit_message_text(
        text=f"Добро пожаловать в главное мнею {call.message.from_user.first_name}",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.kb_main)


#------------------------------------------------Edit------------------------------------------------
# Edit menu
@dp.callback_query_handler(lambda callback: callback.data == "edit")
async def edit_menu(call):
    await bot.edit_message_text(text="Кого хотите отредактировать?", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.edit_menu)


# Back to edit menu / Delete record
@dp.callback_query_handler(lambda callback: callback.data in ["back_menu_edit", "del"], state="*")
async def back_edit_menu(call, state:FSMContext):
    if call.data == "del":
        async with state.proxy() as data:
            table = data["table"]
            record_id = data['id_' + table]
        rus_name = 'студенты' if table == 'students' else 'кураторы'
        func_bot.remove_record(record_id=record_id, table=table)
        text = f'Удаление, {rus_name}'
    else:
        text = 'Меню редактирования'
    await bot.edit_message_text(text=text, message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.edit_menu)
    await state.finish()


# List of all records to edit
@dp.callback_query_handler(lambda callback: callback.data.startswith('all'), state="*")
async def edit_all_records_list(call, state:FSMContext):
    table, rus_name, prefix = ['students', 'студенты', 'std'] if call.data == 'all_std' else ['teachers', 'учителя', 'tch']
    record_id, records_names = func_bot.main_get(tables=[table], columns=['id', 'name'])
    ikb = keyboard.create_ikb_records_list(record_id, records_names, prefix)
    await bot.edit_message_text(
        text=f"Все {rus_name} SkillBox",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)
    await state.finish()


# Show full info about record
@dp.callback_query_handler(lambda callback: callback.data.startswith('std') or callback.data.startswith('tch'), state="*")
async def edit_record_info(call, state:FSMContext):
    table = 'students' if call.data.split('_')[0] == 'std' else 'teachers'
    rec_id = call.data.split('_')[-1]
    text, columns = func_bot.get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await bot.edit_message_text(
        text=text,
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)
    async with state.proxy() as data:
        data[f"id_{table}"] = rec_id
        data["table"] = table

    
# Search records
@dp.callback_query_handler(lambda callback: callback.data.startswith('edit'))
async def search_student_teacher_handler(call, state:FSMContext):
    table, rus_text = ['students', "студента"] if call.data == "edit_std" else ['teachers', "куратора"]
    ikb = keyboard.create_ikb_back_edit_menu(call.data.split('_')[-1])
    await bot.edit_message_text(
        text=f"Введите имя или фамилию {rus_text} которого хотите найти",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)
    async with state.proxy() as data:
        data["table"] = table
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await FSMAdmin.search_name_state.set()


# Show of search results
@dp.message_handler(lambda message: message.text, state=FSMAdmin.search_name_state)
async def search_info_list_student_teacher(message, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        message_id = data["message_search_id"]
        chat_id = data["chat_search_id"]
    records_id, records_name = func_bot.get_search_results(table=table, name=message.text)
    type_class, rus_text = ["std", "Студенты"] if table == 'students' else ["tch", "Кураторы"]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if records_id:
        text = f"{rus_text} по запросу:"
        ikb = keyboard.create_ikb_records_list(records_id, records_name, type_class, True)
        await state.finish()
    else:
        text = "Сходства не найдены, попробуй еще раз или выведи всех:"
        ikb = keyboard.create_ikb_back_edit_menu(type_class)
        await FSMAdmin.search_name_state.set()
    await bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=ikb)


@dp.callback_query_handler(lambda callback: callback.data.startswith("feat_"))
async def edit_record_feat(call, state:FSMContext):
    _, rec_id, feat_name, feat_name_rus, table = call.data.split("_")
    ikb = keyboard.create_ikb_back_rec_info(rec_id, table)
    await bot.edit_message_text(
        text=f"Введите изменение значении {feat_name_rus}",
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)
    async with state.proxy() as data:
        data["edit_call_message_id"] = call.message.message_id
        data["edit_call_chat_id"] = call.message.chat.id
        data["params"] = [rec_id, feat_name, table, feat_name_rus]
        await FSMAdmin.edit_records_state.set()

@dp.message_handler(lambda message: message.text, state=FSMAdmin.edit_records_state)
async def edit_recod(message, state:FSMContext):
    async with state.proxy() as data:
        params = data["params"]
        message_id = data["edit_call_message_id"]
        chat_id = data["edit_call_chat_id"]
        data["answer"] = message.text
        rec_id, feat_name, table, feat_name_rus = params
    text_info = func_bot.get_info_list(rec_id, table=table)[0]
    old_value = "".join([i.split(" - ")[1] for i in text_info.splitlines() if feat_name_rus in i.split(" - ")])
    async with state.proxy() as data:
        data["old_value"] = old_value
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.edit_message_text(
        text=f"Вы точно хотите изменить {old_value} на {message.text}",
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=keyboard.accept_and_reject_edit)

@dp.callback_query_handler(lambda callback: callback.data in ["accept_edit", "reject_edit"], state=FSMAdmin.edit_records_state)
async def recject_or_accept_edit(call, state:FSMContext):
    async with state.proxy() as data:
        params = data["params"]
        answer = data["answer"]
        old_value = data["old_value"]
    rec_id, feat_name, table, name_rus = params
    if call.data == "accept_edit":
        func_bot.passing_func(table, rec_id, answer)
    #Функция изменения данных по дб
    text, columns = func_bot.get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await bot.edit_message_text(
        text=text,
        message_id=call.message.message_id,
        chat_id=call.message.chat.id,
        reply_markup=ikb)
    await state.finish()


#------------------------------------------------Add------------------------------------------------

# Add menu
@dp.callback_query_handler(lambda callback: callback.data in ["add", "back_menu"], state="*")
async def add_menu(call, state:FSMContext):
    await bot.edit_message_text(text="*Инструкция по добавлению*", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.add_menu)
    if call.data != "add":
        await state.finish()


# Request name of record
@dp.callback_query_handler(lambda callback: callback.data.startswith('add_'))
async def request_name(call, state:FSMContext):
    postfix = call.data.split('_')[-1]
    table, rus_name = ['students', 'студента'] if postfix == "std" else ['teachers', 'куратора']
    await bot.edit_message_text(text=f"Введите имя {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_add_menu)
    async with state.proxy() as data:
        data["message_id_" + postfix] = call.message.message_id
        data["chat_id_" + postfix] = call.message.chat.id
        data["table"] = table
    await FSMAdmin.state_name.set()


# Request direction of record
@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_name)
async def request_prof(message, state:FSMContext):
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
            ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof')
            await bot.edit_message_text(text=f"Хорошо, теперь выбери {mini_text}", message_id=message_id, chat_id=chat_id, reply_markup=ikb)
            await FSMAdmin.next()
            await FSMAdmin.next()
        else:
            await bot.edit_message_text(text=f"Введите названия направления куратора", message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_add_menu)
            async with state.proxy() as data:
                data["call_message_id_tch"] = message_id
                data["call_chat_id_tch"] = chat_id
            await FSMAdmin.state_prof.set()
    elif status[1] == "normal":
        await bot.edit_message_text(text=status[0], message_id=message_id, chat_id=chat_id, reply_markup=keyboard.yes_and_no)
        await FSMAdmin.next()
    else:
        await bot.edit_message_text(text=status[0], message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_add_menu)
        await FSMAdmin.next()


# Input proccesing (fignya)
@dp.callback_query_handler(lambda callback: callback.data in ["yes", "no"], state=FSMAdmin.state_yes_and_no)
async def input_processing(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        directions_id, directions_names = func_bot.main_get(tables=['teachers'], columns=['id', 'direction'])
        ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof')
    rus_name = 'студента' if table == 'students' else 'куратора'
    if call.data == "yes":
        if table == 'students':
            await bot.edit_message_text(text=f"Хорошо, теперь выбери профессию {rus_name}", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=ikb)
            await FSMAdmin.next()
        else:
            await bot.edit_message_text(text=f"Введите названия направления куратора", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_add_menu)
            async with state.proxy() as data:
                data["call_message_id_tch"] = call.message.message_id
                data["call_chat_id_tch"] = call.message.chat.id
            await FSMAdmin.state_prof.set()
    else:
        await bot.edit_message_text(text=f"Введите имя {rus_name}", message_id=call.message.message_id,chat_id=call.message.chat.id, reply_markup=keyboard.back_add_menu)
        await FSMAdmin.state_name.set()


# Request tg-id for new teacher
@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_prof)
async def request_tg_id_tch(message, state:FSMContext):
    async with state.proxy() as data:
        message_id = data["call_message_id_tch"]
        chat_id = data["call_chat_id_tch"]
        data["prof"] = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.edit_message_text(text=f"Теперь введи ТГ id куратора", message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_add_menu)
    await FSMAdmin.state_tg_name.set()


# Request tg-id for new student
@dp.callback_query_handler(lambda callback: callback.data.startswith('prof'), state=FSMAdmin.state_prof)
async def request_tg_id_std(call, state:FSMContext):
    await bot.edit_message_text(text=f"Теперь введи ТГ id студента", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.back_add_menu)
    async with state.proxy() as data:
        data['prof'] = call.data.split('_')[-1]
        data["call_message_id_std"] = call.message.message_id
        data["call_chat_id_std"] = call.message.chat.id
    await FSMAdmin.next()


# Show list with new record info
@dp.message_handler(lambda message: message.text, state=FSMAdmin.state_tg_name)
async def list_adding_info(message, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    postfix, rus_name = ['std', 'Студента'] if table == 'students' else ['tch', 'Куратора']
    async with state.proxy() as data:
        name = data["name_" + postfix]
        if table == 'students':
            teacher_name, direction = func_bot.main_get(tables=['teachers'], columns=["name", 'direction'], condition=f"id = {data['prof']}", is_one=True)
        else:
            direction = data["prof"]
            teacher_name = ""
        data["tg_id_" + postfix] = message.text
        message_id_call = data["call_message_id_" + postfix]
        chat_id_call = data["call_chat_id_" + postfix]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.edit_message_text(text=f"Информация о введённых данных\n\n{rus_name} - {name}\nГруппа - {direction}\nКуратор - {teacher_name}\nТГ ник - {message.text}", chat_id=chat_id_call, message_id=message_id_call, reply_markup=keyboard.accept_and_reject)
    await FSMAdmin.next()


# Accept or reject adding / Back to add menu
@dp.callback_query_handler(lambda callback: callback.data in ["accept", "reject"] or callback.data in ["accept_2", "reject_2"], state=FSMAdmin.accept_or_reject)
async def add_or_back_menu(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    postfix, rus_name = ['std', 'Студент'] if table == 'students' else ['tch', 'Куратор']
    if call.data == "accept":
        async with state.proxy() as data:
            name = data["name_" + postfix]
            tg_id = data["tg_id_" + postfix]
            if table == 'students':
                direction = data['prof']
                params = {"name": f"'{name}'", "score": 0, "teacher_id": direction, 'tg_id': tg_id}
            else:
                direction = data["prof"]
                params = {"name": f"'{name}'", "direction": f"'{direction}'", 'tg_id': tg_id}
        func_bot.add_record(table=table, params=params)
        await bot.edit_message_text(text=f"{rus_name} {name} успешно добавлен\nХотите ещё что-то добавить?", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.add_menu)
        await state.finish()
    else:
        await bot.edit_message_text(text="*Инструкция по добавлению*", message_id=call.message.message_id, chat_id=call.message.chat.id, reply_markup=keyboard.add_menu)
    await state.finish()

