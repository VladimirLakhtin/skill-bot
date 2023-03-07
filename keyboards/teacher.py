from aiogram.types import InlineKeyboardMarkup,  InlineKeyboardButton


# Main menu
kb_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить студента ➕", callback_data="add_std"), InlineKeyboardButton("Редактировать студентов 🖋", callback_data="edit_std")],
    [InlineKeyboardButton("Добавить SkillCoins 💎", callback_data="coins_add"), InlineKeyboardButton("Топ студентов", callback_data="top_std")]
])


# Back main menu
back_main_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("Назад в меню", callback_data="back_main_menu")]])


# Add Students

accept_or_reject = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅ Принять ✅", callback_data="accept"), InlineKeyboardButton("❌ Отмена ❌", callback_data="reject")]
])


# Edit Students

def back_edit_menu(students):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Показать всех 🔍", callback_data="all"), InlineKeyboardButton("🔙 Назад в меню", callback_data='back_main_menu')]
    ])


def create_ikb_records_list(rec_id=[], rec_names=[], is_all=False) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    for i, name in zip(rec_id, rec_names):
        ikb.add(InlineKeyboardButton(name + " 🪪", callback_data=f"std_{i}"))
    if is_all:
        ikb.add(InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main_menu"))
    else:
        ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data="all"), InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main_menu"))
    return ikb


def create_ikb_info_list(rec_id: int, columns: dict) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Имя', callback_data=f"feat_{rec_id}_name_Имя"), InlineKeyboardButton('User name', callback_data=f"feat_{rec_id}_tg-username_User-name")],
        [InlineKeyboardButton('SkillCoins', callback_data=f"feat_{rec_id}_score_SkillCoins")],
        [InlineKeyboardButton("Удалить 🗑", callback_data="del"), InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main_menu")]
    ])
    return ikb


def create_ikb_back_rec_info(rec_id):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔙 Назад", callback_data= f"std_{rec_id}")]])
    return ikb


def accept_and_reject_edit():
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅ Принять ✅", callback_data="accept_edit"), InlineKeyboardButton("❌ Отмена ❌", callback_data="reject_edit")]
])


# Add SkillCoins

def students_list(rec_id=None, rec_names=None, is_all=False) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_names:
        for i, name in zip(rec_id, rec_names):
            ikb.add(InlineKeyboardButton(name, callback_data=f'choose_std_{i}_{name}'))
    if is_all:
        ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    else:
        ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data='allstd4tch'), InlineKeyboardButton("🔙 Назад в меню", callback_data='back_main_menu'))
    return ikb


def tasks_list(rec_id=None, rec_title=None, rec_cost=None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_title and rec_cost:
        for i, title, cost in zip(rec_id, rec_title, rec_cost):
            ikb.add(InlineKeyboardButton(title, callback_data=f'choose_task_{i}_{title}_{cost}'))
    ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    return ikb


def accept_add_coins():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Добавить ✅", callback_data="coins_add_accept"), InlineKeyboardButton("❌ Отмена ❌", callback_data="back_main_menu")],
    ])