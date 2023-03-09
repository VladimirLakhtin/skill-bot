from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Main menu
kb_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить студента ➕", callback_data="add_std"),
     InlineKeyboardButton("Редактировать студентов 🖋", callback_data="edit_std")],
    [InlineKeyboardButton("Добавить SkillCoins 💎", callback_data="coins_add"),
     InlineKeyboardButton("Топ студентов", callback_data="top_std")]
])

# Back main menu
back_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton("Назад в меню", callback_data="back_main_menu")]])

# Add Students

# Request accept or reject add new student
accept_or_reject = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅ Принять ✅", callback_data="accept"),
     InlineKeyboardButton("❌ Отмена ❌", callback_data="reject")]
])


# Edit Students

# Edit menu
def back_edit_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Показать всех 🔍", callback_data="all"),
         InlineKeyboardButton("🔙 Назад в меню", callback_data='back_main_menu')]
    ])


# Show result of search or all students
def create_ikb_records_list(rec_id: List = None, rec_names: List = None, is_all=False,
                            is_edit=True) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    for i, name in zip(rec_id, rec_names):
        cb_data = f'std_{i}' if is_edit else f'choose_std_{i}_{name}'
        ikb.add(InlineKeyboardButton(name + " 🪪", callback_data=cb_data))
    if is_all:
        ikb.add(InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main_menu"))
    else:
        cb_data = 'all' if is_edit else 'allstd4tch'
        ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data=cb_data),
                InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main_menu"))
    return ikb


# Show student info
def create_ikb_info_list(rec_id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Имя', callback_data=f"feat_{rec_id}_name_Имя"),
         InlineKeyboardButton('User name', callback_data=f"feat_{rec_id}_tg-username_User-name")],
        [InlineKeyboardButton('SkillCoins', callback_data=f"feat_{rec_id}_score_SkillCoins")],
        [InlineKeyboardButton("Удалить 🗑", callback_data="del"),
         InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main_menu")]
    ])
    return ikb


# Back to student info
def create_ikb_back_rec_info(rec_id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔙 Назад", callback_data=f"std_{rec_id}")]])
    return ikb


# Request accept or reject edit student feat
def accept_and_reject_edit() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Принять ✅", callback_data="accept_edit"),
         InlineKeyboardButton("❌ Отмена ❌", callback_data="reject_edit")]
    ])


# Add SkillCoins

# Show all teacher's students
def students_list(rec_id: int = None, rec_names: str = None, is_all: bool = False) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_names:
        for i, name in zip(rec_id, rec_names):
            ikb.add(InlineKeyboardButton(name, callback_data=f'choose_std_{i}_{name}'))
    if is_all:
        ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    else:
        ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data='allstd4tch'),
                InlineKeyboardButton("🔙 Назад в меню", callback_data='back_main_menu'))
    return ikb


# Show tasks list to add SkillCoins
def tasks_list(rec_id: int = None, rec_title: str = None, rec_cost: int = None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_title and rec_cost:
        for i, title, cost in zip(rec_id, rec_title, rec_cost):
            ikb.add(InlineKeyboardButton(title, callback_data=f'choose_task_{i}_{title}_{cost}'))
    ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    return ikb


# Confirm
def accept_add_coins() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Добавить ✅", callback_data="coins_add_accept"),
         InlineKeyboardButton("❌ Отмена ❌", callback_data="back_main_menu")],
    ])
