import config
import data_checking
import func_bot
import keyboards.developer_keyboards as keyboard
from handlers.admin_handlers import bot, dp
from state import FSMDeveloper, FSMContext
import asyncio



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

@dp.callback_query_handler(lambda callback: callback.data == "back_dev_main_menu", state=[FSMDeveloper.add_id_admin_state, FSMDeveloper.add_name_admin_state, None])
async def start_handler(call, state:FSMContext):
   await main_edit_mes("Главное меню разработчика", call=call, ikb=keyboard.get_main_menu_developer())
   await state.finish()


@dp.callback_query_handler(lambda callback: callback.data == 'get_file_db')
async def get_db_file(call):
   with open("db.db", "rb") as file:
      path = file.read()
   await bot.send_document(call.message.chat.id, ('db.dp', path))


#------------------------------------------------Add------------------------------------------------

@dp.callback_query_handler(lambda callback: callback.data == "admins_add")
async def input_admins_name(call, state:FSMContext):
   await main_edit_mes("Введите имя админа", call=call, ikb=keyboard.back_main_menu_but)
   async with state.proxy() as data:
      data["message_id_admin"] = call.message.message_id
      data["chat_id_admin"] = call.message.chat.id
   await FSMDeveloper.add_name_admin_state.set()

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
   await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)


@dp.callback_query_handler(lambda callback: callback.data in ["accept_add_admin", "reject_add_admin"], state=FSMDeveloper.accept_or_reject_admin_state)
async def accept_or_reject_add_admins(call, state:FSMContext):
   if call.data == "accept_add_admin":
      async with state.proxy() as data:
         name = data["name_admin"]
         id = data["id_admin"]
         prams = {
            "name": f"'{name}'",
            "tg_id": id
         }
      func_bot.add_record(table="admins", params=prams)
      text = f"Админ {name} добавлен"
   else:
      text = "Главное меню разработчика"
   await main_edit_mes(text, call=call, ikb=keyboard.get_main_menu_developer())
   await state.finish()


#------------------------------------------------Edit------------------------------------------------

@dp.callback_query_handler(lambda callback: callback.data == "admins_edit")
async def get_list_admins(call):
   rec_name, rec_id = func_bot.main_get(tables=["admins"], columns=["name", "id"])
   ikb = keyboard.create_list_admins_ikb(records_name=rec_name, rec_id=rec_id)
   await main_edit_mes(text="Все админы", call=call, ikb=ikb)

@dp.callback_query_handler(lambda callback: callback.data.startswith("admins_"), state=[FSMDeveloper.edit_admin_state, None])
async def edit_info_admins(call, state:FSMContext):
   await state.finish()
   _, rec_id = call.data.split("_")
   info_text, colums = func_bot.get_info_list(rec_id, "admins")
   async with state.proxy() as data:
      data["rec_id_admin"] = rec_id
      data["colums_admin"] = colums
   await main_edit_mes(text=info_text, call=call, ikb=keyboard.edit_admin_ikb)

@dp.callback_query_handler(lambda callback: callback.data.startswith("input_"))
async def input_edit(call, state:FSMContext):
   async with state.proxy() as data:
      rec_id = data["rec_id_admin"]
      colums = data["colums_admin"]
      data["edit_admin_message_id"] = call.message.message_id
      data["edit_admin_chat_id"] = call.message.chat.id
      ikb = keyboard.back_edit_admin_ikb(rec_id)
      data["ikb_admin"] = ikb
      tg_id, name = colums
      data["feet_admin"], text = [tg_id, f"Введите новое значение tg-id "] if call.data.split("_")[-1] == "id" else [name, f"Введите новое имя"]
   await main_edit_mes(text=text, call=call, ikb=ikb)
   await FSMDeveloper.edit_admin_state.set()

@dp.message_handler(lambda message: message.text, state=FSMDeveloper.edit_admin_state)
async def edit_record_admin(message, state:FSMContext):
   async with state.proxy() as data:
      feet = data["feet_admin"]
      message_id = data["edit_admin_message_id"]
      chat_id = data["edit_admin_chat_id"]
      rec_id = data["rec_id_admin"]
      ikb = data["ikb_admin"]
   column, feet_name = ["name", "name"] if feet == "name" else ["score", "tg_id"]
   flag, text = data_checking.input_edit(inputs=message.text, column=column)
   if not flag:
      try:
         await main_edit_mes(text=text, chat_id=chat_id, message_id=message_id, ikb=ikb)
      except:
          pass
   else:
      func_bot.update_record("admins", columns={feet_name:message.text}, rec_id=rec_id)
      info_text, _ = func_bot.get_info_list(rec_id, "admins")
      await main_edit_mes(text=info_text, chat_id=chat_id, message_id=message_id, ikb=keyboard.edit_admin_ikb)
      await state.finish()
   await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)


@dp.callback_query_handler(lambda callback: callback.data == "del_admins")
async def del_admin(call, state:FSMContext):
   async with state.proxy() as data:
      rec_id = data["rec_id_admin"]
   func_bot.remove_record(rec_id, "admins")
   rec_name, rec_id = func_bot.main_get(tables=["admins"], columns=["name", "id"])
   ikb = keyboard.create_list_admins_ikb(records_name=rec_name, rec_id=rec_id)
   await main_edit_mes(text="Админ удалён", call=call, ikb=ikb)

