import data_checking
from func_bot import *
import keyboards.developer as keyboard
from create_bot import bot, dp
from state import FSMDeveloper, FSMContext
from filters import IsDeveloper


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data == "admins_edit")
async def get_list_admins(call):
    rec_name, rec_id = main_get(tables=["admins"], columns=["name", "id"])
    ikb = keyboard.create_list_admins_ikb(records_name=rec_name, rec_id=rec_id)
    await main_edit_mes(text="Все админы", call=call, ikb=ikb)


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data.startswith("admins_"), state="*")
async def edit_info_admins(call, state: FSMContext):
    await state.finish()
    _, rec_id = call.data.split("_")
    info_text, colums = get_info_list(rec_id, "admins")
    async with state.proxy() as data:
        data["rec_id_admin"] = rec_id
        data["colums_admin"] = colums
    await main_edit_mes(text=info_text, call=call, ikb=keyboard.edit_admin_ikb)


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data.startswith("input_"))
async def input_edit(call, state: FSMContext):
    async with state.proxy() as data:
        rec_id = data["rec_id_admin"]
        colums = data["colums_admin"]
        data["edit_admin_message_id"] = call.message.message_id
        data["edit_admin_chat_id"] = call.message.chat.id
        ikb = keyboard.back_edit_admin_ikb(rec_id)
        data["ikb_admin"] = ikb
        tg_id, name = colums
        data["feet_admin"], text = [tg_id, f"Введите новое значение tg-id "] if call.data.split("_")[-1] == "id" else [
            name, f"Введите новое имя"]
    await main_edit_mes(text=text, call=call, ikb=ikb)
    await FSMDeveloper.edit_admin_state.set()


@dp.message_handler(IsDeveloper(), lambda message: message.text, state=FSMDeveloper.edit_admin_state)
async def edit_record_admin(message, state: FSMContext):
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
        update_record("admins", columns={feet_name: message.text}, rec_id=rec_id)
        info_text, colums = get_info_list(rec_id, "admins")
        await main_edit_mes(text=info_text, chat_id=chat_id, message_id=message_id, ikb=keyboard.edit_admin_ikb)
        await state.finish()
        async with state.proxy() as data:
            data["rec_id_admin"] = rec_id
            data["colums_admin"] = colums
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data == "del_admins")
async def del_admin(call, state: FSMContext):
    async with state.proxy() as data:
        rec_id = data["rec_id_admin"]
    remove_record(rec_id, "admins")
    rec_name, rec_id = main_get(tables=["admins"], columns=["name", "id"], condition=f"id = {rec_id}", is_one=True)
    ikb = keyboard.create_list_admins_ikb(records_name=rec_name, rec_id=rec_id)
    await main_edit_mes(text="Админ удалён", call=call, ikb=ikb)
