import data_checking
import keyboards.admin_keyboards as keyboard

from create_bot import bot, dp
from state import FSMAddRecord, FSMContext, FSMEditFeat, FSMSeachRecord

import func_bot


async def main_edit_mes(text, ikb, call=None, message_id=None, chat_id=None):
    if message_id == None and call != None:
        message_id = call.message.message_id
    if chat_id == None and call != None:
        chat_id = call.message.chat.id
    await bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=ikb)

#------------------------------------------------Main------------------------------------------------

# Main menu
#@dp.message_handler(commands=['start'])
#async def start_handler(message):
#    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню, {message.from_user.first_name}", reply_markup=keyboard.kb_main)


# Back to main menu
# @dp.callback_query_handler(lambda callback: callback.data == "back_main_menu")
# async def back_main_menu(call, state:FSMContext):
#     await state.finish()
#     text = f"Добро пожаловать в главное мнею {call.message.from_user.first_name}"
#     await main_edit_mes(text=text, ikb=keyboard.kb_main, call=call)


#------------------------------------------------Edit------------------------------------------------
# Edit menu
@dp.callback_query_handler(lambda callback: callback.data == "edit")
async def edit_menu(call):
    text="Кого хотите отредактировать?"
    await main_edit_mes(text=text, ikb=keyboard.edit_menu, call=call)


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
    await main_edit_mes(text=text, ikb=keyboard.edit_menu, call=call)
    await state.finish()


@dp.callback_query_handler(lambda callback: callback.data in ["awards_edit", "tasks_edit"])
async def get_title_list(call, state:FSMContext):
    colum = "title"
    table, text = ["awards", "Список всех наград"] if call.data == "awards_edit" else ["tasks", "Список всех задач"]
    rec_id, records_name = func_bot.main_get(tables=[table], columns=['id', colum])
    ikb = keyboard.create_ikb_records_list(rec_id, records_name, type_class=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["table"] = table

@dp.callback_query_handler(lambda callback: callback.data.startswith("awards") or callback.data.startswith("tasks"), state="*")
async def get_record_info_title(call, state:FSMContext):
    async with state.proxy() as data:
        try:
            table = data["table"]
        except KeyError:
            _, _, table, _ = data["params"]
        rec_id = call.data.split('_')[-1]
        text, columns = func_bot.get_info_list(rec_id, table=table)
        ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
        await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()



# List of all records to edit
@dp.callback_query_handler(lambda callback: callback.data.startswith('all'), state="*")
async def edit_all_records_list(call, state:FSMContext):
    table, rus_name, prefix = ['students', 'студенты', 'std'] if call.data == 'all_std' else ['teachers', 'учителя', 'tch']
    record_id, records_names = func_bot.main_get(tables=[table], columns=['id', 'name'])
    ikb = keyboard.create_ikb_records_list(record_id, records_names, prefix, option="edit")
    text = f"Все {rus_name} SkillBox"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()


# Show full info about record
@dp.callback_query_handler(lambda callback: callback.data.startswith('std') or callback.data.startswith('tch'), state="*")
async def edit_record_info(call, state: FSMContext):
    table = 'students' if call.data.split('_')[0] == 'std' else 'teachers'
    rec_id = call.data.split('_')[-1]
    text, columns = func_bot.get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data[f"id_{table}"] = rec_id
        data["table"] = table

    
# Search records
@dp.callback_query_handler(lambda callback: callback.data.startswith('edit'))
async def search_student_teacher_handler(call, state:FSMContext):
    table, rus_text = ['students', "студента"] if call.data == "edit_std" else ['teachers', "куратора"]
    ikb = keyboard.create_ikb_back_edit_menu(call.data.split('_')[-1])
    text = f"Введите имя или фамилию {rus_text} которого хотите найти"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["table"] = table
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await FSMSeachRecord.search_name_state.set()


# Show of search results
@dp.message_handler(lambda message: message.text, state=FSMSeachRecord.search_name_state)
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
        ikb = keyboard.create_ikb_records_list(records_id, records_name, type_class, "search")
        await state.finish()
    else:
        text = "Сходства не найдены, попробуй еще раз или выведи всех:"
        ikb = keyboard.create_ikb_back_edit_menu(type_class)
        await FSMSeachRecord.search_name_state.set()
    await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)


@dp.callback_query_handler(lambda callback: callback.data.startswith("feat_"))
async def edit_record_feat(call, state:FSMContext):
    _, rec_id, feat_name, feat_name_rus, table = call.data.split("_")
    if table == "students" and feat_name == "direction":
        directions_id, directions_names = func_bot.main_get(tables=['teachers'], columns=['id', 'direction'])
        ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option='edit', std_id=rec_id)
    else:
        ikb = keyboard.create_ikb_back_rec_info(rec_id, table)
    text = f"Введите изменение значении {feat_name_rus}"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["edit_call_message_id"] = call.message.message_id
        data["edit_call_chat_id"] = call.message.chat.id
        data["params"] = [rec_id, feat_name, table, feat_name_rus]
    await FSMEditFeat.edit_records_state.set()


@dp.callback_query_handler(lambda callback: callback.data.startswith("prof_"), state=FSMEditFeat.edit_records_state)
async def edit_student_prof(call, state:FSMContext):
    rec_id_prof = call.data.split("_")[1]
    async with state.proxy() as data:
        rec_id_std = data["params"][0]
        new_value = func_bot.main_get(tables=['teachers'], columns=['direction'], condition=f"id = {rec_id_prof}", is_one=True)
        cur_value = func_bot.main_get(tables=["students", "teachers"], columns=['teachers.direction'], condition=f"students.id = {rec_id_std}", is_one=True)
        data["answer"] = rec_id_prof
    text = f"Вы точно хотите изменить {cur_value} на {new_value}"
    await main_edit_mes(text=text, ikb=keyboard.accept_and_reject_edit, call=call)


@dp.message_handler(lambda message: message.text, state=FSMEditFeat.edit_records_state)
async def edit_record(message, state:FSMContext):
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
        except:
            pass
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    else:
        cur_value = func_bot.main_get(tables=[table], columns=[feat_name], condition=f"id = {rec_id}", is_one=True)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        text = f"Вы точно хотите изменить {cur_value} на {message.text}"
        await main_edit_mes(text=text, ikb=keyboard.accept_and_reject_edit, message_id=message_id, chat_id=chat_id)


@dp.callback_query_handler(lambda callback: callback.data in ["accept_edit", "reject_edit"], state=FSMEditFeat.edit_records_state)
async def reject_or_accept_edit(call, state:FSMContext):
    async with state.proxy() as data:
        params = data["params"]
        answer = data["answer"]
    rec_id, feat_name, table, _ = params
    feat_name = 'teacher_id' if feat_name == 'direction' and table == 'students' else feat_name
    if call.data == "accept_edit":
        func_bot.update_record(table, rec_id, {feat_name: answer})
    text, columns = func_bot.get_info_list(rec_id, table=table)
    ikb = keyboard.create_ikb_info_list(rec_id=rec_id, columns=columns, table=table)
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data['table'] = table
        data['id_' + table] = rec_id 


#------------------------------------------------Add------------------------------------------------

# Add menu
@dp.callback_query_handler(lambda callback: callback.data in ["add", "back_menu"], state="*")
async def add_menu(call, state:FSMContext):
    text = "*Инструкция по добавлению*"
    await main_edit_mes(text=text, ikb=keyboard.add_menu, call=call)
    if call.data != "add":
        await state.finish()


# Request name of record
@dp.callback_query_handler(lambda callback: callback.data.startswith('add_'))
async def request_name(call, state:FSMContext):
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


@dp.message_handler(lambda message: message.text, state=FSMAddRecord.state_title)
async def input_title(message, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        chat_id = data["chat_id_" + table]
        message_id = data["message_id_" + table]
        data["name_" + table] = message.text
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    mini_text = "Введите кол-во Skillcoins для награды" if table == "awards" else "Введите кол-во Skillcoins за выполненое задание"
    await main_edit_mes(text=mini_text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.state_cost.set()

@dp.message_handler(lambda message: message.text, state=FSMAddRecord.state_cost)
async def input_cost(message, state:FSMContext):
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
            text = f"Введите именно число"
            ikb = keyboard.back_add_menu
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        await next_state.set()


# Request direction of record
@dp.message_handler(lambda message: message.text, state=FSMAddRecord.state_name)
async def request_prof(message, state:FSMContext):
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
        directions_id, directions_names = func_bot.main_get(tables=['teachers'], columns=['id', 'direction'])
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        if status[1] == "ok":
            if table == 'students':
                ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option="add")
                text=f"Хорошо, теперь выбери {mini_text}"
                await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)
            elif table == 'teachers':
                await bot.edit_message_text(text=f"Введите названия направления куратора", message_id=message_id, chat_id=chat_id, reply_markup=keyboard.back_add_menu)
                async with state.proxy() as data:
                    data["call_message_id_tch"] = message_id
                    data["call_chat_id_tch"] = chat_id
            await FSMAddRecord.state_prof.set()
        elif status[1] == "normal":
            await main_edit_mes(text=status[0], ikb=keyboard.yes_and_no, message_id=message_id, chat_id=chat_id)
            await FSMAddRecord.next()
        else:
            await main_edit_mes(text=status[0], ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
            await FSMAddRecord.next()


# Input proccesing (fignya)
@dp.callback_query_handler(lambda callback: callback.data in ["yes", "no"], state=FSMAddRecord.state_yes_and_no)
async def input_processing(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        directions_id, directions_names = func_bot.main_get(tables=['teachers'], columns=['id', 'direction'])
        ikb = keyboard.create_ikb_records_list(directions_id, directions_names, type_class='prof', option="add")
    rus_name = 'студента' if table == 'students' else 'куратора'
    if call.data == "yes":
        if table == 'students':
            text=f"Хорошо, теперь выбери профессию {rus_name}"
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
@dp.message_handler(lambda message: message.text, state=FSMAddRecord.state_prof)
async def request_tg_id_tch(message, state:FSMContext):
    async with state.proxy() as data:
        message_id = data["call_message_id_teachers"]
        chat_id = data["call_chat_id_teachers"]
        data["prof"] = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    text = f"Теперь введи ТГ id куратора"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, message_id=message_id, chat_id=chat_id)
    await FSMAddRecord.state_tg_name.set()


# Request tg-id for new student
@dp.callback_query_handler(lambda callback: callback.data.startswith('prof'), state=FSMAddRecord.state_prof)
async def request_tg_id_std(call, state:FSMContext):
    text = f"Теперь введи ТГ id студента"
    await main_edit_mes(text=text, ikb=keyboard.back_add_menu, call=call)
    async with state.proxy() as data:
        data['prof'] = call.data.split('_')[-1]
        data["call_message_id_students"] = call.message.message_id
        data["call_chat_id_students"] = call.message.chat.id
    await FSMAddRecord.next()


# Show list with new record info
@dp.message_handler(lambda message: message.text, state=FSMAddRecord.state_tg_name)
async def list_adding_info(message, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
    rus_name = 'Студента' if table == 'students' else 'Куратора'
    async with state.proxy() as data:
        name = data["name_" + table]
        if table == 'students':
            teacher_name, direction = func_bot.main_get(tables=['teachers'], columns=["name", 'direction'], condition=f"id = {data['prof']}", is_one=True)
        else:
            direction = data["prof"]
            teacher_name = ""
        data["tg_id_" + table] = message.text
        message_id_call = data["call_message_id_" + table]
        chat_id_call = data["call_chat_id_" + table]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    text = f"Информация о введённых данных\n\n{rus_name} - {name}\nГруппа - {direction}\nКуратор - {teacher_name}\nТГ ник - {message.text}"
    await main_edit_mes(text=text, ikb=keyboard.accept_and_reject, message_id=message_id_call, chat_id=chat_id_call)
    await FSMAddRecord.accept_or_reject.set()


# Accept or reject adding / Back to add menu
@dp.callback_query_handler(lambda callback: callback.data in ["accept", "reject"], state=FSMAddRecord.accept_or_reject)
async def add_or_back_menu(call, state:FSMContext):
    async with state.proxy() as data:
        table = data["table"]
        name = data["name_" + table]
        if call.data == "accept":
            if table == 'students':
                rus_name = 'Студент'
                direction = data['prof']
                params = {"name": f"'{name}'", "score": 0, "teacher_id": direction, 'tg_id': data["tg_id_" + table]}
            elif table == "teachers":
                rus_name = "Куратор"
                direction = data["prof"]
                params = {"name": f"'{name}'", "direction": f"'{direction}'", 'tg_id': data["tg_id_" + table]}
            elif table == "awards":
                rus_name = "Награда"
                params = {"title": f"'{name}'", "cost": data["cost_" + table]}
                name = data["name_" + table] + data["cost_" + table]
            else:
                rus_name = "Задача"
                params = {"title": f"'{name}'", "reward": data["cost_" + table]}
                name = data["name_" + table] + data["cost_" + table]
            func_bot.add_record(table=table, params=params)
            text = f"{rus_name} {name} успешно добавлен\nХотите ещё что-то добавить?"
        else:
            text = "*Инструкция по добавлению*"
        await main_edit_mes(text=text, ikb=keyboard.add_menu, call=call)
        await state.finish()

