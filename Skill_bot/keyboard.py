from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup,  InlineKeyboardButton, KeyboardButton

# Кнопки админа
kb_main_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Добавить", callback_data="add"), InlineKeyboardButton("Обновить логи", callback_data="update"), InlineKeyboardButton("Редактировать", callback_data="edit")],
    [InlineKeyboardButton("Получить файл бд", callback_data="file_db")],
])

# Назад и Удалить
back_inline = InlineKeyboardButton("Назад", callback_data="back")
del_inline = InlineKeyboardButton("Удалить", callback_data="del")
butt_back_and_del_prod = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(back_inline, del_inline)

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
        ikb.add(back_inline_menu_edit)
    else:
        ikb.add(back_inline_menu)
    return ikb
    
#Кнопки учителя студента и типа
teacher_inline = InlineKeyboardButton("Учитель", callback_data="teacher")
student_inline = InlineKeyboardButton("Студент", callback_data="student")
type_inline = InlineKeyboardButton("Тип Профессии", callback_data="type")
back_inline_main_menu = InlineKeyboardButton("В главное меню", callback_data="back_main_menu")
student_and_teacher_type = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(student_inline, teacher_inline, type_inline, back_inline_main_menu)

#Кнопки учителя студента
student_and_teacher = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Учитель", callback_data="teacher_2"), InlineKeyboardButton("Студент", callback_data="student_2")], 
    [back_inline_main_menu]
])

#Кнопки да и нет
yes_inline = InlineKeyboardButton("Да", callback_data="yes")
no_inline = InlineKeyboardButton("Нет", callback_data="no")
yes_and_no = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(yes_inline, no_inline)

#Кнопки принять и отменить для добавления студентов
accept_inline = InlineKeyboardButton("Принять", callback_data="accept")
reject_inline = InlineKeyboardButton("Отмена", callback_data="reject")
accept_and_reject = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(accept_inline, reject_inline)

#Кнопки принять и отменить для добавления типа профессии
accept_inline_2 = InlineKeyboardButton("Принять", callback_data="accept_2")
reject_inline_2 = InlineKeyboardButton("Отмена", callback_data="reject_2")
accept_and_reject_2 = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(accept_inline_2, reject_inline_2)

#Кнопки принять и отменить для добавления кураторов
accept_inline_3 = InlineKeyboardButton("Принять", callback_data="accept_3")
reject_inline_3 = InlineKeyboardButton("Отмена", callback_data="reject_3")
accept_and_reject_3 = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(accept_inline_3, reject_inline_3)


