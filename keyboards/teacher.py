from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Main menu
kb_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить студента ➕", callback_data="add_std"),
     InlineKeyboardButton("Редактировать студентов 🖋", callback_data="edit_std")],
    [InlineKeyboardButton("Добавить SkillCoins 💎", callback_data="coins_add"),
     InlineKeyboardButton("Топ студентов 🔥", callback_data="top_std")]
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
def create_ikb_records_list(rec_id: List = None, records_names: List = None, is_all=False,
                            is_edit: bool = True, step: int = None, cur_step: int = None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id or records_names:
        if step:
            # Get records slice
            step_rec_name = records_names[cur_step:step:]
            rec_id = rec_id[cur_step:step:]
            # Create records list
            for i, name in enumerate(step_rec_name):
                cd_data = f'std_{rec_id[i]}' if is_edit else f'choose_std_{rec_id[i]}_{name}'
                ikb.add(InlineKeyboardButton(name + " 🪪", callback_data=cd_data))
            # Create page control buttons
            if cur_step == 0 and len(records_names) > step:
                ikb.add(InlineKeyboardButton("➡", callback_data="next_inline" if is_edit else "next_inline_coins"))
            elif len(records_names) > step:
                ikb.add(InlineKeyboardButton("⬅", callback_data="back_inline" if is_edit else "back_inline_coins"),
                        InlineKeyboardButton("➡", callback_data="next_inline" if is_edit else "next_inline_coins"))
            elif cur_step != 0 and len(records_names) <= step:
                ikb.add(InlineKeyboardButton("⬅", callback_data="back_inline" if is_edit else "back_inline_coins"))
        else:
            # Create records list
            for i, name in zip(rec_id, records_names):
                cb_data = f'std_{i}' if is_edit else f'choose_std_{i}_{name}'
                ikb.add(InlineKeyboardButton(name + " 🪪", callback_data=cb_data))
    if is_all:
        ikb.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_main_menu"))
    else:
        cb_data = 'all' if is_edit else 'allstd4tch'
        ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data=cb_data),
                InlineKeyboardButton("🔙 Главное меню", callback_data="back_main_menu"))
    return ikb


# Show student info
def create_ikb_info_list(rec_id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Имя', callback_data=f"feat_{rec_id}_name_Имя"),
         InlineKeyboardButton('User name', callback_data=f"feat_{rec_id}_tg-username_User-name")],
        [InlineKeyboardButton('SkillCoins', callback_data=f"feat_{rec_id}_score_SkillCoins")],
        [InlineKeyboardButton("Удалить 🗑", callback_data=f"del_confirm_{rec_id}"),
         InlineKeyboardButton("🔙 Назад", callback_data="edit_std")]
    ])
    return ikb


# Confirm delete student
def confirm_delete(std_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🗑 Удалить 🗑", callback_data="del"),
         InlineKeyboardButton("❌ Отмена ❌", callback_data=f"std_{std_id}")]
    ])


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

# Show tasks list to add SkillCoins
def tasks_list(rec_id: int = None, rec_title: str = None, rec_cost: int = None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_title and rec_cost:
        for i, title, cost in zip(rec_id, rec_title, rec_cost):
            ikb.add(InlineKeyboardButton(title, callback_data=f'choose_task_{i}_{title}_{cost}'))
    ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='coins_add'))
    return ikb


# Request an adding date
def set_date():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Оставить сегодняшнюю", callback_data="old"),
         InlineKeyboardButton("Задать другую", callback_data="new")],
    ])


# Confirm
def accept_add_coins() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Добавить ✅", callback_data="coins_add_accept"),
         InlineKeyboardButton("❌ Отмена ❌", callback_data="back_main_menu")],
    ])

