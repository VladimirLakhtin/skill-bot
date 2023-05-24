import random

import keyboards.student as keyboard
from func_bot import *
from filters import IsStudent
from create_bot import dp
from script_text.student import text


# Cheak SkillCoins account
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='cheak'))
async def cheak_account(call):
    score = main_get(tables=['students'], columns=['score'], condition=f'tg_id = {call.message.chat.id}')[0]
    if score > 0:
        cur_text = random.choice(text['balance']).format(score)
    else:
        cur_text = text['balance_0']
    await main_edit_mes(text=cur_text, ikb=keyboard.get_back(), call=call)


# Ways to earn SkillCoins list
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='earn'))
async def ways_to_earn(call):
    cur_text = 'Ways to earn'
    await main_edit_mes(text=random.choice(text['earn']), ikb=keyboard.get_records_list('tasks'), call=call)


# Get info about task
@dp.callback_query_handler(IsStudent(), keyboard.cd_earn.filter())
async def get_task_info(call, callback_data: dict):
    description = main_get(tables=['tasks'], columns=['description'],
                           condition=f"id = {callback_data['id']}", is_one=True)
    cur_text = f"<b>{callback_data['title']}</b>\n\n{description}"
    await main_edit_mes(text=cur_text,
                        ikb=keyboard.back_tasks_list(),
                        call=call)