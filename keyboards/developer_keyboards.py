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
        [InlineKeyboardButton("Принять", callback_data="accept_add_admin"), InlineKeyboardButton("Редактировать админа", callback_data="reject_add_admin")]])


def create_list_admins_ikb(admins):
    ikb = InlineKeyboardMarkup()
    for i in admins.keys():
        ikb.add(InlineKeyboardButton(admins[i], callback_data=f"admins_{i}_{admins[i]}"))
    ikb.add(back_main_menu_but)
    return ikb

edit_admin_ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Имя", callback_data="name_admin_edit"), InlineKeyboardButton("ID", callback_data="id_admin_edit")],[InlineKeyboardButton("Назад", callback_data="admins_edit")],
        [InlineKeyboardButton("Удалить", callback_data="del_admins")]])