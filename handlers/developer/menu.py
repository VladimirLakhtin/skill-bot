from func_bot import *
import keyboards.developer_keyboards as keyboard
from create_bot import bot, dp
from state import FSMDeveloper, FSMContext
from filters import IsDeveloper


@dp.message_handler(IsDeveloper(), commands=['start'])
async def start_handler(message):
   await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню разработчика, {message.from_user.first_name}", reply_markup=keyboard.get_main_menu_developer())

@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data == "back_dev_main_menu", state=[FSMDeveloper.add_id_admin_state, FSMDeveloper.add_name_admin_state, None])
async def start_handler(call, state:FSMContext):
   await main_edit_mes("Главное меню разработчика", call=call, ikb=keyboard.get_main_menu_developer())
   await state.finish()
