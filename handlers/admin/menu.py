from func_bot import *
from create_bot import bot, dp
import keyboards.admin as keyboard
from state import FSMContext
from filters import IsAdmin
from text import text_admin


@dp.message_handler(IsAdmin(), commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id,
                           f"Добро пожаловать в главное меню, {message.from_user.first_name}\n{text_admin.text['start']}",
                           reply_markup=keyboard.kb_main)


# Back to main menu
@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data == "back_main_menu", state="*")
async def back_main_menu(call, state: FSMContext):
    await state.finish()
    text = f"Главное меню\n{text_admin.text['start']}"
    await main_edit_mes(text=text, ikb=keyboard.kb_main, call=call)
