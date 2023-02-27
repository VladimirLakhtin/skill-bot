import data_checking
import keyboards.teacher_keyboards as keyboard
import keyboards.admin_keyboards as adm_keyboard
from handlers.admin_handlers import bot, dp
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
@dp.message_handler(commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню, {message.from_user.first_name}", reply_markup=keyboard.get_main_menu())


# Back to main menu
@dp.callback_query_handler(text='back_main_menu')
async def back_main_tch_menu(call):
    text = f"Добро пожаловать в главное меню {call.message.from_user.first_name}"
    await main_edit_mes(text=text, ikb=keyboard.get_main_menu(), call=call)


# Search students
@dp.callback_query_handler(text='coins_add')
async def search_student_handler(call, state:FSMContext):
    ikb = keyboard.create_ikb_back_edit_menu('std')
    text = f"Введите имя или фамилию студента которого хотите найти:"
    await main_edit_mes(text=text, ikb=ikb, call=call)
    async with state.proxy() as data:
        data["message_search_id"] = call.message.message_id
        data["chat_search_id"] = call.message.chat.id
    await FSMSeachRecord.search_name_state.set()


# Show of search results
@dp.message_handler(lambda message: message.text, state=FSMSeachRecord.search_name_state)
async def search_result_student(message, state:FSMContext):
    async with state.proxy() as data:
        message_id = data["message_search_id"]
        chat_id = data["chat_search_id"]
    records_id, records_name = func_bot.get_search_results(table='students', name=message.text)
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if records_id:
        text = f"Сутденты по запросу:"
        ikb = adm_keyboard.create_ikb_records_list(records_id, records_name, 'std', "search")
        await state.finish()
    else:
        text = "Сходства не найдены, попробуй еще раз или выведи всех:"
        ikb = adm_keyboard.create_ikb_back_edit_menu('std')
        await FSMSeachRecord.search_name_state.set()
    await main_edit_mes(text=text, ikb=ikb, message_id=message_id, chat_id=chat_id)






