from func_bot import *
from create_bot import bot, dp
import keyboards.teacher as keyboard
from state import FSMContext
from filters import IsTeacher
from text import text_admin


# Main menu
@dp.message_handler(IsTeacher(), commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id,
                           f"Добро пожаловать в главное меню, {message.from_user.first_name}\n{text_admin.text['start']}",
                           reply_markup=keyboard.kb_main)


# Back to main menu
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data in ["back_main_menu", 'del'], state="*")
async def back_main_menu(call, state: FSMContext):
    if call.data == 'del':
        async with state.proxy() as data:
            rec_id = data['id']
        remove_record(record_id=rec_id, table='students')
    await state.finish()
    text = f"Главное меню\n{text_admin.text['start']}"
    await main_edit_mes(text=text, ikb=keyboard.kb_main, call=call)
