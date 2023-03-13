from func_bot import *
from create_bot import bot, dp
import keyboards.teacher as keyboard
from state import FSMContext
from filters import IsTeacher
from script_text.teacher import text


# Main menu
@dp.message_handler(IsTeacher(), commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, text['start'], reply_markup=keyboard.kb_main, parse_mode='html')


# Back to main menu
@dp.callback_query_handler(IsTeacher(), lambda callback: callback.data in ["back_main_menu", 'del'], state="*")
async def back_main_menu(call, state: FSMContext):
    if call.data == 'del':
        async with state.proxy() as data:
            rec_id = data['id']
        remove_record(record_id=rec_id, table='students')
        await call.answer("Студент удален")
    await state.finish()
    await main_edit_mes(text=text['start'], ikb=keyboard.kb_main, call=call)
