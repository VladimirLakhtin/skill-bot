from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton
from aiogram.utils.callback_data import CallbackData
import func_bot



def get_main_menu_developer():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Добавить админа", callback_data="admins_add"), InlineKeyboardButton("Редактировать админа", callback_data="admins_edit")],
        [InlineKeyboardButton('Получить файл DB', callback_data='get_file_db')],
    ])

back_main_menu_but = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Назад в главное меню", callback_data="back_dev_main_menu")]
    ])

accept_or_reject_add_admin = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Принять", callback_data="accept_add_admin"), InlineKeyboardButton("Отменить", callback_data="reject_add_admin")]])


def create_list_admins_ikb(records_name, rec_id):
    ikb = InlineKeyboardMarkup()
    for i, name in enumerate(records_name):
        ikb.add(InlineKeyboardButton(name, callback_data=f"admins_{rec_id[i]}"))
    ikb.add(InlineKeyboardButton("Назад в главное меню", callback_data="back_dev_main_menu"))
    return ikb


def back_edit_admin_ikb(rec_id):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Назад", callback_data=f"admins_{rec_id}")]])
    return ikb

edit_admin_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Имя", callback_data="input_name"), InlineKeyboardButton("ID", callback_data="input_id")],[InlineKeyboardButton("Назад", callback_data="admins_edit")],
        [InlineKeyboardButton("Удалить", callback_data="del_admins")]])