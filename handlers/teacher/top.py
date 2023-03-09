import func_bot
from func_bot import *
from create_bot import dp
import keyboards.admin as keyboard
from filters import IsTeacher


@dp.callback_query_handler(IsTeacher(), text="top_std")
async def top_list(call):
    teacher_id = main_get(tables=['teachers'], columns=['id'], condition=f'tg_id = {call.from_user.id}', is_one=True)
    top_student = func_bot.get_top_std(teacher_id)
    text = 'Топ 10 студентов по SkillCoins'
    for i in top_student:
        text += f"\n {i[0]} - {i[1]}"
    await main_edit_mes(text=text, ikb=keyboard.back_main_menu, call=call)
