from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import func_bot

# CallbackData
cd_main_menu = CallbackData('main_menu_std', 'chapter')
cd_spend = CallbackData('spend_list', 'id', 'title', 'cost')
cd_earn = CallbackData('earn_list', 'id', 'title', 'reward')
cd_purchase = CallbackData('purchase_accept', 'id', 'title', 'cost')
cd_top= CallbackData('top')


# Main menu
def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Как заработать? 📌', callback_data=cd_main_menu.new('earn')),
         InlineKeyboardButton('Потратить 💳', callback_data=cd_main_menu.new('spend'))],
        [InlineKeyboardButton('Проверить счёт 💰', callback_data=cd_main_menu.new('cheak')),
         InlineKeyboardButton('Топ студентов 🔥', callback_data=cd_top.new())],
    ])


# Back to main menu
def get_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('🔙 Назад', callback_data=cd_main_menu.new('menu'))]
    ])


# List of tasks or awards
def get_records_list(table: str) -> InlineKeyboardMarkup:
    column_3, cd = ['cost', cd_spend] if table == 'awards' else ['reward', cd_earn]
    rec_id, titles, costs = func_bot.main_get(tables=[table], columns=['id', 'title', column_3])
    ikb = InlineKeyboardMarkup()
    for i, id in enumerate(rec_id):
        ikb.add(InlineKeyboardButton(titles[i] + ' ' + str(costs[i]) + " 💸",
                                     callback_data=cd.new(id, titles[i], costs[i])))
    ikb.add(InlineKeyboardButton('🔙 Назад', callback_data=cd_main_menu.new('menu')))
    return ikb


# Confirm with spend SkillCoins
def get_confirmation(rec_id: int, title: str, cost: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Купить 💸', callback_data=cd_purchase.new(id=rec_id, title=title, cost=cost)),
         InlineKeyboardButton('Отмена ❌', callback_data=cd_main_menu.new('spend'))]
    ])


# Exit from a task info
def back_tasks_list() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data=cd_main_menu.new('earn')))