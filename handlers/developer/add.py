import data_checking
from func_bot import *
import keyboards.developer as keyboard
from create_bot import bot, dp
from state import FSMDeveloper, FSMContext
from filters import IsDeveloper


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data == "admins_add")
async def input_admins_name(call, state: FSMContext):
    await main_edit_mes("Введите имя админа", call=call, ikb=keyboard.back_main_menu_but)
    async with state.proxy() as data:
        data["message_id_admin"] = call.message.message_id
        data["chat_id_admin"] = call.message.chat.id
    await FSMDeveloper.add_name_admin_state.set()


@dp.message_handler(IsDeveloper(), lambda message: message.text, state=FSMDeveloper.add_name_admin_state)
async def add_name_admin(message, state: FSMContext):
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
        await main_edit_mes(text="Хорошо теперь введи id админа", chat_id=chat_id, message_id=message_id,
                            ikb=keyboard.back_main_menu_but)
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)


@dp.message_handler(IsDeveloper(), lambda message: message.text, state=FSMDeveloper.add_id_admin_state)
async def add_id_admin(message, state: FSMContext):
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
        await main_edit_mes(text=f"Имя админа: {name}\nID админа: {message.text}", chat_id=chat_id,
                            message_id=message_id, ikb=keyboard.confirm_add_admin)
        await FSMDeveloper.next()
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data in ["accept_add_admin", "reject_add_admin"],
                           state=FSMDeveloper.accept_or_reject_admin_state)
async def confirm_add_admins(call, state: FSMContext):
    if call.data == "accept_add_admin":
        async with state.proxy() as data:
            name = data["name_admin"]
            id = data["id_admin"]
            prams = {
                "name": f"'{name}'",
                "tg_id": id
            }
        add_record(table="admins", params=prams)
        text = f"Админ {name} добавлен"
    else:
        text = "Главное меню разработчика"
    await main_edit_mes(text, call=call, ikb=keyboard.get_main_menu_developer())
    await state.finish()
