import keyboards.student as keyboard
from func_bot import *
from filters import IsStudent
from create_bot import dp
from script_text.student import text


# Main menu
@dp.message_handler(IsStudent(), commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id,
                           text['start'],
                           reply_markup=keyboard.get_main_menu())


# Back to main menu
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='menu'))
async def back_main_menu(call):
    await main_edit_mes(text=text['start'], ikb=keyboard.get_main_menu(), call=call)
