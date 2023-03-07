import keyboards.student_keyboards as keyboard
from create_bot import dp
from func_bot import *
from filters import IsStudent

# Ways to spend SkillCoins list
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='spend'))
async def ways_to_spend(call):
    text = 'Spend, please ->'
    await main_edit_mes(text=text, ikb=keyboard.get_list_spend(), call=call)


# Accept or reject purchase
@dp.callback_query_handler(IsStudent(), keyboard.cd_spend.filter())
async def purchase_confirmation(call, callback_data: dict):
    score = main_get(tables=['students'], columns=['score'], condition=f'tg_id = {call.message.chat.id}')[0]
    if score >= int(callback_data['cost']):
        text = 'Yes or not'
        await main_edit_mes(text=text, ikb=keyboard.get_confirmation(callback_data['id'], callback_data['title'], callback_data['cost']), call=call)
    else:
        await call.answer('Недостаточно средств')


# Purchase end and back to spend menu
@dp.callback_query_handler(IsStudent(), keyboard.cd_purchase.filter())
async def purchse_end(call, callback_data):
    cost, title = callback_data['cost'], callback_data['title']
    std_id, score, name = main_get(tables=['students'], columns=['id', 'score', "name"], condition=f'tg_id = {call.message.chat.id}')
    update_record(table='students', rec_id=std_id[0], columns={'score': score[0] - int(cost)})
    text_admin = f"{name[0]} Потратил {cost} на {title}"
    await bot.send_message(text=text_admin, chat_id="-1001881010069")
    text = f'Purchase is done: {callback_data["title"]}\nSpend, please ->'
    await main_edit_mes(text=text, ikb=keyboard.get_list_spend(), call=call)