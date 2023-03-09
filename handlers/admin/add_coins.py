import keyboards.admin as keyboard
from state import FSMContext, FSMSeachStudent
from func_bot import *
from filters import IsAdmin
from text import text_admin
import random


# Search students
@dp.callback_query_handler(IsAdmin(), text='coins_add')
async def search_student_handler(call, state: FSMContext):
    ikb = keyboard.students_list()
    text = f"Введите имя или фамилию студента которого хотите найти:"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await call.answer("Поисковая система включена")
    await FSMSeachStudent.search_name_state.set()


# Show of search results
@dp.message_handler(IsAdmin(), lambda message: message.text, state=FSMSeachStudent.search_name_state)
async def search_result_student(message, state: FSMContext):
    async with state.proxy() as data:
        message_id = data["message_search_id"]
        chat_id = data["chat_search_id"]
    records_id, records_name = get_search_results(table='students', name=message.text)
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    ikb = keyboard.students_list(records_id, records_name)
    if records_id:
        text = f"Сутденты по запросу:"
        await state.finish()
    else:
        text = "Сходства не найдены, попробуй еще раз или выведи всех:"
        await FSMSeachStudent.search_name_state.set()
    await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)


# Show all
@dp.callback_query_handler(IsAdmin(), text='allstd4tch', state=FSMSeachStudent.search_name_state)
async def all_student(call, state: FSMContext):
    record_id, records_names = main_get(tables=['students'], columns=['id', 'name'])
    ikb = keyboard.students_list(record_id, records_names, is_all=True)
    text = f"Все студенты SkillBox"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    await state.finish()


# Choose student
@dp.callback_query_handler(IsAdmin(), lambda call: call.data.startswith('choose_std'))
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        data['std_info'] = call.data.split('_')[2:]
    task_id, task_titles, cost = main_get(tables=['tasks'])
    ikb = keyboard.tasks_list(task_id, task_titles, cost)
    text = 'Теперь выбери причину начисления:'
    await main_edit_mes(text=text, ikb=ikb, call=call)


# Accept adding SkillCoins
@dp.callback_query_handler(IsAdmin(), lambda call: call.data.startswith('choose_task'))
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        _, std_name = data['std_info']
        data['task_info'] = call.data.split('_')[2:]
    ikb = keyboard.accept_add_coins()
    text = f'Хотите добавить SkillCoins {std_name} за {call.data.split("_")[3]} - {call.data.split("_")[4]} SkillCoins'
    await main_edit_mes(text=text, ikb=ikb, call=call)


# Add SkillCoins
@dp.callback_query_handler(IsAdmin(), text='coins_add_accept')
async def choose_task(call, state: FSMContext):
    async with state.proxy() as data:
        std_id, _ = data['std_info']
        _, _, cost = data['task_info']
    await call.answer(f"{cost} SkillCoins зачислено")
    add_skillcoins(std_id=std_id, coins=cost)
    text = f"Главное меню\n{text_admin.text['start']}"
    await main_edit_mes(text=text, ikb=keyboard.kb_main, call=call)
