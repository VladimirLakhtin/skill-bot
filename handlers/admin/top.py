import func_bot
from func_bot import *
from create_bot import dp
import keyboards.admin as keyboard
from filters import IsAdmin


@dp.callback_query_handler(IsAdmin(), lambda callback: callback.data == "top")
async def top_list(call):
    top_student = func_bot.get_top_std()
    text = 'Топ 10 студентов по SkillCoins'
    for i in top_student:
        text += f"\n {i[0]} - {i[1]}"
    await main_edit_mes(text=text, ikb=keyboard.back_main_menu, call=call)
