from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Main menu
kb_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить ➕", callback_data="add"),
     InlineKeyboardButton("Редактировать 🖋", callback_data="edit")],
    [InlineKeyboardButton("Добавить SkillCoins 💎", callback_data="coins_add"),
     InlineKeyboardButton("Топ студентов 🔥", callback_data="top")]
])

back_add_menu_btn = InlineKeyboardButton("🔙 Назад в меню", callback_data="back_menu")
back_main_menu_btn = InlineKeyboardButton("В главное меню 🏠", callback_data="back_main_menu")
back_main_menu = InlineKeyboardMarkup(inline_keyboard=[[back_main_menu_btn]])

# Add

# Add menu
add_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратор 💼", callback_data="add_teachers"),
     InlineKeyboardButton("Студент 👤", callback_data="add_students")],
    [InlineKeyboardButton("Награду 💰", callback_data="add_awards"),
     InlineKeyboardButton("Задания 📎", callback_data="add_tasks")],
    [InlineKeyboardButton("В главное меню 🏠", callback_data="back_main_menu")]
])

# Accept or reject add
accept_and_reject = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅ Принять ✅", callback_data="accept"),
     InlineKeyboardButton("❌ Отмена ❌", callback_data="reject")]
])

# Back main menu
back_add_menu = InlineKeyboardMarkup(inline_keyboard=[[back_add_menu_btn]])

# Edit

# Edit menu
edit_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратор 💼", callback_data="edit_tch"),
     InlineKeyboardButton("Студент 👤", callback_data="edit_std")],
    [InlineKeyboardButton("Награду 💰", callback_data="awards_edit"),
     InlineKeyboardButton("Задания 📎", callback_data="tasks_edit")],
    [back_main_menu_btn]
])

# Search edit menu
def create_ikb_back_edit_menu(type_class: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Показать всех 🔍", callback_data="all_" + type_class),
         InlineKeyboardButton("🔙 Назад в меню", callback_data='back_menu_edit')]
    ])


# Back to main menu or delete record
butt_back_and_del_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Удалить ➕🗑", callback_data="del_search")],
    [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_menu_edit")]
])


# Records list
def create_ikb_records_list(rec_id: List[int], records_names: List[str], type_class: str, option: str = None,
                            std_id: int = None, step: int = None, cur_step: int = None, pref: str = None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if step:
        try:
            if cur_step > step:
                step_rec_name = records_names[cur_step:step:-1]
                rec_id = rec_id[cur_step:step:-1]
            else:
                step_rec_name = records_names[cur_step:step]
                rec_id = rec_id[cur_step:step]
        except IndexError:
            if len(records_names) < step:
                step_rec_name = records_names
                rec_id = rec_id
            else:
                step_rec_name = records_names[step:]
                rec_id = rec_id[step:]
        for i, name in enumerate(step_rec_name):
            ikb.add(InlineKeyboardButton(name + " 🪪", callback_data=f"{type_class}_{rec_id[i]}"))
        if cur_step == 0:
            ikb.add(InlineKeyboardButton("➡", callback_data="next_inline"))
        elif len(records_names) > step:
            ikb.add(InlineKeyboardButton("⬅", callback_data="back_inline"), InlineKeyboardButton("➡", callback_data="next_inline"))
        else:
            ikb.add(InlineKeyboardButton("⬅", callback_data="back_inline"))
    else:
        for i, name in enumerate(records_names):
            ikb.add(InlineKeyboardButton(name + " 🪪", callback_data=f"{type_class}_{rec_id[i]}"))
    if pref:
        back_edit = InlineKeyboardButton("🔙 Назад в меню", callback_data=f"edit_{pref}")
    else:
        back_edit = InlineKeyboardButton("🔙 Назад в меню", callback_data="back_menu_edit")
    if type_class == "awards" or type_class == "tasks":
        ikb.add(back_edit)
    elif type_class != 'prof':
        if option == 'search':
            ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data="all_" + type_class),
                    InlineKeyboardButton("🔙 Назад в меню", callback_data="back_menu_edit"))
        elif option == 'edit':
            ikb.add(back_edit)
    elif type_class == "prof":
        if option == 'add':
            ikb.add(back_add_menu_btn)
        elif option == 'edit':
            ikb.add(InlineKeyboardButton("🔙 Назад", callback_data=f"{'std'}_{std_id}"))
    return ikb


# Full info about record
def create_ikb_info_list(rec_id: int, columns: dict, table: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    count = 0
    for feat in columns:
        count += 1
        btn = InlineKeyboardButton(columns[feat], callback_data=f"feat_{rec_id}_{feat}_{columns[feat]}_{table}")
        if count % 2 == 0:
            ikb.add(prev_btn, btn)
        prev_btn = btn
    pref_1 = ""
    pref_2 = ""
    if table != 'students':
        ikb.add(prev_btn)
    if table == "teachers":
        ikb.row(InlineKeyboardButton("🔙 Назад в меню", callback_data="edit_tch"))
    else:
        if table == "awards":
            pref_1 = "awards"
            pref_2 = "edit"
        elif table == "students":
            pref_1 = "edit"
            pref_2 = "std"
        else:
            pref_1 = "tasks"
            pref_2 = "edit"
        ikb.row(InlineKeyboardButton("Удалить ➕🗑", callback_data="del"),
                InlineKeyboardButton("🔙 Назад в меню", callback_data=f"{pref_1}_{pref_2}"))
    return ikb


#
def create_ikb_back_rec_info(rec_id: int, table: str) -> InlineKeyboardMarkup:
    if table == "students":
        type_class = "std"
    elif table == "teachers":
        type_class = "tch"
    elif table == "awards":
        type_class = "awards"
    else:
        type_class = "tasks"
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔙 Назад", callback_data=f"{type_class}_{rec_id}")]])
    return ikb


# Accept or reject edit
accept_and_reject_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅ Принять ✅", callback_data="accept_edit"),
     InlineKeyboardButton("❌ Отмена ❌", callback_data="reject_edit")]])


# Add SkillCoins

# Students list
def students_list(rec_id: List[int] = None, rec_names: List[str] = None, is_all: bool = False) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_names:
        for i, name in zip(rec_id, rec_names):
            ikb.add(InlineKeyboardButton(name, callback_data=f'choose_std_{i}_{name}'))
    if is_all:
        ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    else:
        ikb.row(InlineKeyboardButton("Показать всех 🔍", callback_data='allstd4tch'),
                InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    return ikb


# List of awards or tasks
def tasks_list(rec_id: List[int] = None, rec_title: List[str] = None,
               rec_cost: List[int] = None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if rec_id and rec_title and rec_cost:
        for i, title, cost in zip(rec_id, rec_title, rec_cost):
            ikb.add(InlineKeyboardButton(title, callback_data=f'choose_task_{i}_{title}_{cost}'))
    ikb.add(InlineKeyboardButton("🔙 Назад", callback_data='back_main_menu'))
    return ikb


# Accept or reject add SkillCoins
def accept_add_coins() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Добавить ✅", callback_data="coins_add_accept"),
         InlineKeyboardButton("❌ Отмена ❌", callback_data="back_main_menu")],
    ])


# Input control
yes_and_no = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅", callback_data="yes"), InlineKeyboardButton("❌", callback_data="no")],
])

yes_and_no_del = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("✅", callback_data="yes_del"), InlineKeyboardButton("❌", callback_data="no_del")],
])