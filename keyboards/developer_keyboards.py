from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton
from aiogram.utils.callback_data import CallbackData
import func_bot



def get_main_menu_developer():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Добавить админа", callback_data="admins_add"), InlineKeyboardButton("Редактировать админа", callback_data="admins_edit")],
        [InlineKeyboardButton('Получить файл DB', callback_data='get_file_db')],
    ])

