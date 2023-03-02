import keyboards.student_keyboards as keyboard
from func_bot import *
from filters import IsStudent
import text.text_student
# Main menu
@dp.message_handler(IsStudent(), commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню, {message.from_user.first_name}\n{text.text_student.text['start']}", reply_markup=keyboard.get_main_menu())


# Back to main menu
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='menu'))
async def back_main_menu(call):
    text_menu = f"Главное меню\n{text.text_student.text['start']}"
    await main_edit_mes(text=text_menu, ikb=keyboard.get_main_menu(), call=call)