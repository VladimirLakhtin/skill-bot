from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton
from aiogram.utils.callback_data import CallbackData
import func_bot


def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Добавить", callback_data="add_students"), InlineKeyboardButton("Редактировать", callback_data="edit_std")],
        [InlineKeyboardButton('Добавить SkillCoins', callback_data='coins_add')],
    ])

def create_ikb_records_list(rec_id, records_names, type_class, option=None, std_id=None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    for i, name in enumerate(records_names):
        ikb.add(InlineKeyboardButton(name, callback_data=f"_{rec_id[i]}"))
    back_edit = InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit")
    ikb.row(InlineKeyboardButton("Показать всех", callback_data="all_" + type_class), InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit"))