from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton
from aiogram.utils.callback_data import CallbackData
import func_bot


cd_main_menu = CallbackData('main_menu_std', 'chapter')
cd_spend = CallbackData('spend_list', 'id', 'title', 'cost')
cd_purchase = CallbackData('purchase_accept', 'id', 'title', 'cost')


def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Как заработать?', callback_data=cd_main_menu.new('earn')), InlineKeyboardButton('Потратить', callback_data=cd_main_menu.new('spend'))],
        [InlineKeyboardButton('Проверить счёт', callback_data=cd_main_menu.new('cheak'))],
    ])


def get_list_spend():
    rec_id, titles, costs = func_bot.main_get(tables=['awards'], columns=['id', 'title', 'cost'])
    ikb = InlineKeyboardMarkup()
    for i, id in enumerate(rec_id):
        ikb.add(InlineKeyboardButton(titles[i] + ' ' + str(costs[i]), callback_data=cd_spend.new(id=id, title=titles[i], cost=costs[i])))
    ikb.add(InlineKeyboardButton('Назад', callback_data=cd_main_menu.new('menu')))
    return ikb 


def get_back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Назад', callback_data=cd_main_menu.new('menu'))]
    ])


def get_confirmation(id, title, cost):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Купить', callback_data=cd_purchase.new(id=id, title=title, cost=cost)), 
         InlineKeyboardButton('Отмена', callback_data=cd_main_menu.new('spend'))]
    ])