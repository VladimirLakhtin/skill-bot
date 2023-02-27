from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton
from aiogram.utils.callback_data import CallbackData
import func_bot


def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Добавить", callback_data="add"), InlineKeyboardButton("Редактировать", callback_data="edit")],
        [InlineKeyboardButton('Добавить SkillCoins', callback_data='add_coins')],
    ])
