from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton

# Кнопки админа
kb_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить", callback_data="add"), InlineKeyboardButton("Обновить логи", callback_data="update"), InlineKeyboardButton("Редактировать", callback_data="edit")],
    [InlineKeyboardButton("Получить файл бд", callback_data="file_db")],
])

# Назад и Удалить
butt_back_and_del_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Удалить", callback_data="del_search")],
    [InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit")]
])


def create_ikb_back_edit_menu(type_class: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Показать всех", callback_data="all_" + type_class), InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit")]
    ])


#Назад в обычное меню
back_add_menu_btn = InlineKeyboardButton("Назад в меню", callback_data="back_menu")
back_add_menu = InlineKeyboardMarkup(inline_keyboard=[[back_add_menu_btn]])


#Создание кнопок списка
def create_ikb_records_list(record_id, records_names, type_class, is_search=False) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    for i, name in enumerate(records_names):
        ikb.add(InlineKeyboardButton(name, callback_data=f"{type_class}_{record_id[i]}"))
    if type_class != 'prof': 
        if is_search:
            ikb.row(InlineKeyboardButton("Показать всех", callback_data="all_" + type_class), InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit"))
        else:
            ikb.add(InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit"))
    else:
        ikb.add(back_add_menu_btn)
    return ikb


def create_ikb_info_list(rec_id: int, columns: list) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    translate = {
        'Имя': 'name',
        'User-id': 'tg_id',
        'User-name': 'tg_user_name',
        'Профессия': 'direction',
        'Куратор': 'name',
        'SkillCoins': 'account'
    }
    for i, feat in enumerate(columns):
        if (i + 1) % 2 == 0:
            ikb.add(prev_btn, InlineKeyboardButton(feat, callback_data=f"feat_{rec_id}_{translate[feat]}"))
        prev_btn = InlineKeyboardButton(feat, callback_data=f"feat_{rec_id}")
    ikb.row(InlineKeyboardButton("Удалить", callback_data="del"), InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit"))
    return ikb

    
#Кнопки учителя студента и типа
back_main_menu_btn = InlineKeyboardButton("В главное меню", callback_data="back_main_menu")
add_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратор", callback_data="add_tch"), InlineKeyboardButton("Студент", callback_data="add_std")],
    [InlineKeyboardButton("В главное меню", callback_data="back_main_menu")]
])

#Кнопки учителя студента поиска
edit_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратор", callback_data="edit_tch"), InlineKeyboardButton("Студент", callback_data="edit_std")],
    [back_main_menu_btn]
])

#Кнопки выбора поиска
student_and_teacher_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратора", callback_data="teacher_search"), InlineKeyboardButton("Студента", callback_data="student_search")],
    [InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit")]
])


#Кнопки да и нет
yes_and_no = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Да", callback_data="yes"), InlineKeyboardButton("Нет", callback_data="no")],
])

#Кнопки принять и отменить для добавления студентов
accept_and_reject = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Принять", callback_data="accept"), InlineKeyboardButton("Отмена", callback_data="reject")]
])

#Кнопки принять и отменить для добавления кураторов
accept_and_reject_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Принять", callback_data="accept_3"), InlineKeyboardButton("Отмена", callback_data="reject_3")]
])



