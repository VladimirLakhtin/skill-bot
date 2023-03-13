import func_bot
from func_bot import *
from create_bot import dp
import keyboards.student as keyboard
from filters import IsStudent


@dp.callback_query_handler(IsStudent(), keyboard.cd_top.filter())
async def top_list(call):
    top_student = func_bot.get_top_std()
    text = '<b>Топ 10 студентов по SkillCoins 🔥</b>\n'
    for i in top_student:
        text += f"\n {i[0]} - {i[1]}"
    await main_edit_mes(text=text, ikb=keyboard.get_back(), call=call)
