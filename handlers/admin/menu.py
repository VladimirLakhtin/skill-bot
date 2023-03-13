from func_bot import *
from create_bot import bot, dp
import keyboards.admin as keyboard
from state import FSMContext
from filters import IsAdmin
from script_text.admin import text


@dp.message_handler(IsAdmin(), commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, text['start'], reply_markup=keyboard.kb_main, parse_mode='html')


# Back to main menu
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data == "back_main_menu", state="*")
async def back_main_menu(call, state: FSMContext):
    await state.finish()
    await main_edit_mes(text=text['start'], ikb=keyboard.kb_main, call=call)
