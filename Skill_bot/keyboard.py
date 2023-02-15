from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton

# Кнопки админа
ka_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить", callback_data="add"), InlineKeyboardButton("Обновить логи", callback_data="update"), InlineKeyboardButton("Редактировать", callback_data="edit")],
    [InlineKeyboardButton("Получить файл бд", callback_data="file_db")],
])

# Назад и Удалить
butt_back_and_del_search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Удалить", callback_data="del_search")],
    [InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit")]
])

# Назад и Удалить
butt_back_and_del_prod = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Назад", callback_data="back"), InlineKeyboardButton("Удалить", callback_data="del")]
])

#Назад в обычное меню
back_inline_menu = InlineKeyboardButton("Назад в меню", callback_data="back_menu")
back_inline_menu_butt = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(back_inline_menu)

#Создание кнопок списка
def create_ikb(records, type_class):
    ikb = InlineKeyboardMarkup()
    back_inline_menu_edit = InlineKeyboardButton("Назад в меню", callback_data="back_menu_edit")
    for i, std in enumerate(records):
        ikb.add(InlineKeyboardButton(std, callback_data=f"{type_class}_{i + 1}"))
    if type_class == 'type': 
        ikb.add(back_inline_menu)
    else:
        ikb.add(back_inline_menu_edit)
    return ikb
    
#Кнопки учителя студента и типа
back_inline_main_menu = InlineKeyboardButton("В главное меню", callback_data="back_main_menu")
student_and_teacher_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратор", callback_data="teacher"), InlineKeyboardButton("Студент", callback_data="student"),InlineKeyboardButton("Тип Профессии", callback_data="type")],
    [InlineKeyboardButton("В главное меню", callback_data="back_main_menu")]
])

#Кнопки учителя студента поиска
student_and_teacher = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Куратор", callback_data="teacher_2"), InlineKeyboardButton("Студент", callback_data="student_2"), InlineKeyboardButton("Поиск", callback_data="search")],
    [back_inline_main_menu]
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

#Кнопки принять и отменить для добавления типа профессии
accept_and_reject_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Принять", callback_data="accept_2"), InlineKeyboardButton("Отмена", callback_data="reject_2")]
])

#Кнопки принять и отменить для добавления кураторов
accept_and_reject_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Принять", callback_data="accept_3"), InlineKeyboardButton("Отмена", callback_data="reject_3")]
])



