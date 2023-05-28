from create_bot import dp
import keyboards.admin as keyboard
from state import FSMContext, FSMSeachStudent
from func_bot import *
from filters import IsAdmin
from script_text.admin import text
from datetime import date


# Search students
@dp.callback_query_handler(IsAdmin(), text='coins_add')
async def search_student_handler(call, state: FSMContext):
    ikb = keyboard.students_list()
    text = f"Введите <b>имя или фамилию</b> студента которого хотите найти:"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["message_search_id"], data["chat_search_id"] = call.message.message_id, call.message.chat.id
        data["std_choice"] = {}
    await call.answer("Поисковая система включена")
    await FSMSeachStudent.search_name_state.set()


# Show of search results
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMSeachStudent.search_name_state)
async def search_result_student(message, state: FSMContext):
    async with state.proxy() as data:
        message_id, chat_id = data["message_search_id"], data["chat_search_id"]
        std_choice = data["std_choice"]
        records_id, records_name = get_search_results(table='students', name=message.text)
        data['records_info'] = [records_id, records_name]
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    ikb = keyboard.students_list(records_id, records_name, std_choice=std_choice)
    if records_id:
        text = f"<b>Сутденты</b> по запросу:"
    else:
        text = "Сходства не найдены, попробуте еще раз или <b>выведите всех</b>:"
    await FSMSeachStudent.search_name_state.set()
    await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)


# Show all students
@dp.callback_query_handler(IsAdmin(), text='allstd4tch', state=FSMSeachStudent.search_name_state)
async def all_student(call, state: FSMContext):
    async with state.proxy() as data:
        std_choice = data['std_choice']
    record_id, records_names = main_get(tables=['students'], columns=['id', 'name'])
    step, cur_step = 10, 0
    ikb = keyboard.create_ikb_records_list(record_id, records_names, 'std', option='coins',
                                           step=step, cur_step=cur_step, std_choice=[])
    text = f"<b>Все студенты</b> SkillBox"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["next_inline"] = [record_id, records_names, step, cur_step]
        data['std_choice'] = std_choice


# Get next or previous page of students list
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data in ["next_inline_coins", "back_inline_coins"], state="*")
async def next_inline(call, state: FSMContext):
    async with state.proxy() as data:
        record_id, records_names, step, cur_step = data["next_inline"]
        std_choice = data["std_choice"]
    diff = 10 if call.data == "next_inline_coins" else -10
    step += diff
    cur_step += diff
    ikb = keyboard.create_ikb_records_list(record_id, records_names, 'std', option="coins",
                                           step=step, cur_step=cur_step, std_choice=std_choice)
    text = f"Все студенты SkillBox {round(step / 10)} страница"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()
    async with state.proxy() as data:
        data["next_inline"] = [record_id, records_names, step, cur_step]
        data["std_choice"] = std_choice


# Choose student
@dp.callback_query_handler(IsAdmin(), lambda call: call.data.startswith('choose_std'), state="*")
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
            ikb = keyboard.create_ikb_records_list(record_id, records_names, 'std', option="coins",
                                                   step=step, cur_step=cur_step, std_choice=std_choice)
            await main_edit_mes(text=text, ikb=ikb, call=call)
        else:
            message_id, chat_id = data["message_search_id"], data["chat_search_id"]
            records_id, records_name = data['records_info']
            text = 'Студенты по запросу:'
            ikb = keyboard.students_list(records_id, records_name, std_choice=std_choice)
            await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)


# Choose task
@dp.callback_query_handler(IsAdmin(), text='submit_std_list', state="*")
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        std_choice = data['std_choice']
    if std_choice:
        task_id, task_titles, cost, _ = main_get(tables=['tasks'])
        ikb = keyboard.tasks_list(task_id, task_titles, cost)
        text = 'Теперь выбери <b>причину начисления</b>:'
        await main_edit_mes(text=text, ikb=ikb, call=call)
        await state.finish()
        async with state.proxy() as data:
            data['std_choice'] = std_choice
    else:
        await call.answer('Выберите хотя бы одного студента')


# Accept adding SkillCoins
@dp.callback_query_handler(IsAdmin(), lambda call: call.data.startswith('choose_task'))
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        std_choice = data['std_choice']
        data['task_info'] = call.data.split('_')[2:]
    ikb = keyboard.accept_add_coins()
    std_names = ', '.join(std_choice.values())
    text = f'Хотите добавить SkillCoins {std_names} за {call.data.split("_")[3]} - {call.data.split("_")[4]} SkillCoins'
    await main_edit_mes(text=text, ikb=ikb, call=call)


# Add SkillCoins
@dp.callback_query_handler(IsAdmin(), text='coins_add_accept')
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        std_id, std_names = data['std_choice'].keys(), ', '.join(data['std_choice'].values())
        _, tasks_name, cost = data['task_info']
    name_admin = main_get(tables=['admins'], columns=['name'], condition=f'tg_id = {call.from_user.id}', is_one=True)
    log_text = text['log_add'].format(adm=name_admin, std=std_names, score=cost, task=tasks_name, date=date.today().strftime("%d.%m.%Y"))
    await bot.send_message(text=log_text, chat_id="-1001881010069", parse_mode='html')
    await call.answer(f"{cost} SkillCoins зачислено")
    for i in std_id:
        add_skillcoins(std_id=i, coins=cost)
    await main_edit_mes(text=text['start'], ikb=keyboard.kb_main, call=call)
