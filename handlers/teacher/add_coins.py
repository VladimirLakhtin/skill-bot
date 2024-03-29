from aiogram.utils.exceptions import MessageNotModified

import data_checking
import keyboards.teacher as keyboard
from state import FSMContext, FSMSeachStudent, FSMTeachers
from func_bot import *
from filters import IsTeacher
from script_text.teacher import text
from create_bot import dp
from datetime import date


# Search students
@dp.callback_query_handler(IsTeacher(), text='coins_add')
async def search_student_handler(call, state: FSMContext):
    ikb = keyboard.create_ikb_records_list(is_edit=False)
    text = f"Введите <b>имя или фамилию</b> студента которого хотите найти:"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["message_search_id"], data["chat_search_id"] = call.message.message_id, call.message.chat.id
        data["std_choice"] = {}
    await call.answer("Поисковая система включена")
    await FSMSeachStudent.search_name_state.set()


# Show of search results
@dp.message_handler(IsTeacher(), lambda message: message.text, state=FSMSeachStudent.search_name_state)
async def search_result_student(message, state: FSMContext):
    async with state.proxy() as data:
        message_id, chat_id = data["message_search_id"], data["chat_search_id"]
        std_choice = data["std_choice"]
        teacher_id = main_get(tables=['teachers'], columns=['id'], condition=f'tg_id = {message.from_user.id}', is_one=True)
        records_id, records_name = get_search_results(table='students', name=message.text, teacher_id=teacher_id)
        data['records_info'] = [records_id, records_name]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    ikb = keyboard.create_ikb_records_list(records_id, records_name, is_edit=False, std_choice=std_choice)
    if records_id:
        text = f"<b>Сутденты</b> по запросу:"
    else:
        text = "Сходства не найдены, попробуйте еще раз или <b>выведите всех</b>:"
        await FSMSeachStudent.search_name_state.set()
    await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)


# Show all students
@dp.callback_query_handler(IsTeacher(), text='allstd4tch', state=FSMSeachStudent.search_name_state)
async def all_student(call, state: FSMContext):
    async with state.proxy() as data:
        std_choice = data['std_choice']
    teacher_id = main_get(tables=['teachers'], columns=['id'], condition=f'tg_id = {call.from_user.id}', is_one=True)
    record_id, records_names = main_get(tables=['students'], columns=['id', 'name'],
                                        condition=f'teacher_id = {teacher_id}', sort_by='name')
    step, cur_step = 10, 0
    ikb = keyboard.create_ikb_records_list(record_id, records_names, is_all=True,
                                           is_edit=False, step=step, cur_step=cur_step, std_choice=std_choice)
    text = f"<b>Все ваши студенты</b> SkillBox"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["next_inline"] = record_id, records_names, step, cur_step
        data['std_choice'] = std_choice

# Get next or previous page of students list
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data in ["next_inline_coins", "back_inline_coins"], state="*")
async def next_inline(call, state: FSMContext):
    async with state.proxy() as data:
        record_id, records_names, step, cur_step = data["next_inline"]
        std_choice = data["std_choice"]
    diff = 10 if call.data == "next_inline_coins" else -10
    step += diff
    cur_step += diff
    ikb = keyboard.create_ikb_records_list(record_id, records_names, step=step, cur_step=cur_step,
                                           is_all=True, is_edit=False, std_choice=std_choice)
    text = f"Все ваши студенты SkillBox {round(step / 10)} страница"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["next_inline"] = [record_id, records_names, step, cur_step]
        data['std_choice'] = std_choice


# Choose student
@dp.callback_query_handler(IsTeacher(), lambda call: call.data.startswith('choose_std'), state="*")
async def add_student_to_list(call, state: FSMContext):
    async with state.proxy() as data:
        std_id, std_name = int(call.data.split('_')[2]), call.data.split('_')[3]
        if std_id in data["std_choice"]:
            del data["std_choice"][std_id]
        else:
            data["std_choice"][std_id] = std_name
        std_choice = data["std_choice"]

        if 'next_inline' in data:
            record_id, records_names, step, cur_step = data["next_inline"]
            text = f"Все студенты SkillBox {round(step / 10)} страница"
            ikb = keyboard.create_ikb_records_list(record_id, records_names, step=step, cur_step=cur_step,
                                                   is_all=True, is_edit=False, std_choice=std_choice)
            await main_edit_mes(text=text, ikb=ikb, call=call)
        else:
            message_id, chat_id = data["message_search_id"], data["chat_search_id"]
            records_id, records_name = data['records_info']
            text = 'Студенты по запросу:'
            ikb = keyboard.create_ikb_records_list(records_id, records_name, is_edit=False, std_choice=std_choice)
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)


# Choose task
@dp.callback_query_handler(IsTeacher(), text='submit_std_list', state='*')
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        std_choice = data['std_choice']
    if std_choice:
        task_id, task_titles, cost, _ = main_get(tables=['tasks'])
        ikb = keyboard.tasks_list(task_id, task_titles, cost)
        text = 'Теперь выберите <b>причину начисления</b>:'
        await main_edit_mes(text=text, ikb=ikb, call=call)
        await state.finish()
        async with state.proxy() as data:
            data['std_choice'] = std_choice
    else:
        await call.answer('Выберите хотя бы одного студента')


# Accept adding SkillCoins
@dp.callback_query_handler(IsTeacher(), lambda call: call.data.startswith('choose_task'))
async def request_date(call, state: FSMContext):
    async with state.proxy() as data:
        data['task_info'] = call.data.split('_')[2:]
        data["choose"] = call.data
    ikb = keyboard.set_date()
    text = "Хотите ли вы добавить <b>дату начисления</b>?"
    await main_edit_mes(text=text, ikb=ikb, call=call)


@dp.callback_query_handler(IsTeacher(), lambda call: call.data in ["new", "old"])
async def request_date(call, state: FSMContext):
    async with state.proxy() as data:
        std_names = ', '.join(data['std_choice'].values())
        info = data["choose"]
        data["mess_id"] = call.message.message_id
        data["chat_id"] = call.message.chat.id
        if call.data == "old":
            text = f'Хотите добавить SkillCoins ' \
                   f'\n<b>{std_names}</b> за {info.split("_")[3]} - <b>{info.split("_")[4]}</b> SkillCoins ' \
                   f'\n<b>{date.today().strftime("%d.%m.%Y")}</b>?'
            ikb = keyboard.accept_add_coins()
            await main_edit_mes(text=text, ikb=ikb, call=call)
            await FSMTeachers.add_coins_state.set()
            data["date"] = date.today().strftime("%d.%m.%Y")
        else:
            await main_edit_mes(text="Введите <b>дату начисления</b> в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>",
                                ikb=keyboard.back_main_menu, call=call)
            await FSMTeachers.add_day_state.set()


@dp.message_handler(IsTeacher(), lambda message: message.text, state=FSMTeachers.add_day_state)
async def days(message, state: FSMContext):
    async with state.proxy() as data:
        std_names = ', '.join(data['std_choice'].values())
        info = data["choose"]
        message_id = data["mess_id"]
        chat_id = data["chat_id"]
        flag, text = data_checking.input_edit(message.text, 'date')
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        if not flag:
            try:
                await main_edit_mes(text=text, message_id=message_id, chat_id=chat_id, ikb=keyboard.back_main_menu)
                await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
            except MessageNotModified:
                pass
            await FSMTeachers.add_day_state.set()
        else:
            await main_edit_mes(f'Хотите добавить SkillCoins '
                                f'\n<b>{std_names}</b> за {info.split("_")[3]} - <b>{info.split("_")[4]}</b> SkillCoins'
                                f'\n<b>{message.text}</b>?',
                                message_id=message_id, chat_id=chat_id, ikb=keyboard.accept_add_coins())
            data["date"] = message.text
            await FSMTeachers.next()


# Add SkillCoins
@dp.callback_query_handler(IsTeacher(), text='coins_add_accept', state=FSMTeachers.add_coins_state)
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        std_id, std_names = data['std_choice'].keys(), ', '.join(data['std_choice'].values())
        _, tasks_name, cost = data['task_info']
        dates = data["date"]
    await call.answer(f"{cost} SkillCoins зачислено")
    name_teacher = main_get(tables=['teachers'], columns=['name'], condition=f'tg_id = {call.from_user.id}', is_one=True)
    log_text = text['log_add'].format(tch=name_teacher, std=std_names, score=cost, task=tasks_name, date=dates)
    await bot.send_message(text=log_text, chat_id="-1001881010069", parse_mode='html')
    for i in std_id:
        add_skillcoins(std_id=i, coins=cost)
    await main_edit_mes(text=text['start'], ikb=keyboard.kb_main, call=call)
    await state.finish()
