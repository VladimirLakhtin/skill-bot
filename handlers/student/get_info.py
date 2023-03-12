import keyboards.student as keyboard
from func_bot import *
from filters import IsStudent
from create_bot import dp


# Cheak SkillCoins account
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='cheak'))
async def cheak_account(call):
    score = main_get(tables=['students'], columns=['score'], condition=f'tg_id = {call.message.chat.id}')[0]
    await main_edit_mes(text=f'Твой счёт: {score}', ikb=keyboard.get_back(), call=call)


# Ways to earn SkillCoins list
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='earn'))
async def ways_to_earn(call):
    text = 'Ways to earn'
    await main_edit_mes(text=text, ikb=keyboard.get_back(), call=call)
