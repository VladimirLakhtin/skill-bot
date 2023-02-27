import data_checking
import keyboards.developer_keyboards as keyboard
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
@dp.message_handler(commands=['start'])
async def start_handler(message):
   await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню разработчика, {message.from_user.first_name}", reply_markup=)

@dp.message_handler(lambda callback: callback.data == "back_dev_main_menu")
async def start_handler(call):
   await main_edit_mes("Главное меню разработчика", call=call, ikb=)

@dp.callback_query_handler(lambda callback: callback.data == "admins_add")
async def add_admins_id(call):

