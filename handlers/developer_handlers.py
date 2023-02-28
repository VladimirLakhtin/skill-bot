import config
import data_checking
import keyboards.developer_keyboards as keyboard
import keyboards.admin_keyboards as adm_keyboard
from handlers.admin_handlers import bot, dp
from state import FSMDeveloper, FSMContext


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
   await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню разработчика, {message.from_user.first_name}", reply_markup=keyboard.get_main_menu_developer())

@dp.message_handler(lambda callback: callback.data == "back_dev_main_menu")
async def start_handler(call, state:FSMContext):
   await state.finish()
   await main_edit_mes("Главное меню разработчика", call=call, ikb=keyboard.get_main_menu_developer())

@dp.callback_query_handler(lambda callback: callback.data == "admins_add")
async def input_admins_name(call, state:FSMContext):
   await main_edit_mes("Введите имя админа", call=call, ikb=keyboard.back_main_menu_but)
   await FSMDeveloper.add_name_admin_state.set()
   async with state.proxy() as data:
      data["message_id_admin"] = call.message.message_id
      data["chat_id_admin"] = call.message.chat.id

@dp.message_handler(lambda message: message.text, state=FSMDeveloper.add_name_admin_state)
async def add_name_admin(message, state:FSMContext):
   async with state.proxy() as data:
      chat_id = data["chat_id_admin"]
      message_id = data["message_id_admin"]
   flag, text = data_checking.input_edit(inputs=message.text, column="name")
   if not flag:
      try:
         await main_edit_mes(text=text, chat_id=chat_id, message_id=message_id, ikb=keyboard.back_main_menu_but)
      except:
         pass
   else:
      async with state.proxy() as data:
         data["name_admin"] = message.text
      await FSMDeveloper.next()
      await main_edit_mes(text="Хорошо теперь введи id админа", chat_id=chat_id, message_id=message_id, ikb=keyboard.back_main_menu_but)
   await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)


@dp.message_handler(lambda message: message.text, state=FSMDeveloper.add_id_admin_state)
async def add_id_admin(message, state:FSMContext):
   async with state.proxy() as data:
      chat_id = data["chat_id_admin"]
      message_id = data["message_id_admin"]
      name = data["name_admin"]
   flag, text = data_checking.input_edit(inputs=message.text, column="score")
   if not flag:
      try:
         await main_edit_mes(text=text, chat_id=chat_id, message_id=message_id, ikb=keyboard.back_main_menu_but)
      except:
         pass
   else:
      async with state.proxy() as data:
         data["id_admin"] = message.text
      await main_edit_mes(text=f"Имя админа: {name}\nID админа: {message.text}", chat_id=chat_id, message_id=message_id, ikb=keyboard.accept_or_reject_add_admin)
      await FSMDeveloper.next()


@dp.callback_query_handler(lambda callback: callback.data in ["accept_add_admin", "reject_add_admin"], state=FSMDeveloper.accept_or_reject_admin_state)
async def accept_or_reject_add_admins(call, state:FSMContext):
   if call.data == "accept_add_admin":
      async with state.proxy() as data:
         name = data["name_admin"]
         id = data["id_admin"]
      config.ADMINS[id] = name
      text = f"Админ {name} добавлен"
   else:
      text = "Главное меню разработчика"
      await state.finish()
   await main_edit_mes(text, call=call, ikb=keyboard.get_main_menu_developer())



@dp.callback_query_handlers(lambda callback: callback.data == "admins_edit")
async def get_list_admins(call):
   ikb = keyboard.create_list_admins_ikb(config.ADMINS)
   await main_edit_mes(text="Все админы", call=call, ikb=ikb)

@dp.callback_query_handlers(lambda callback: callback.data.startswith("admin_"))
async def edit_info_admins(call):
   _, id, name = call.data.split("_")
   await main_edit_mes(f"Информация об админе\nИмя: {name}\nTG-ID: {id}", call=call, ikb=keyboard.edit_admin_ikb)
