import random
from datetime import date

import keyboards.student as keyboard
from create_bot import dp
from func_bot import *
from filters import IsStudent
from script_text.student import text


# Ways to spend SkillCoins list
@dp.callback_query_handler(IsStudent(), keyboard.cd_main_menu.filter(chapter='spend'))
async def ways_to_spend(call):
    await main_edit_mes(random.choice(text['spend']), ikb=keyboard.get_records_list('awards'), call=call)


# Get info about award. Accept or reject purchase
@dp.callback_query_handler(IsStudent(), keyboard.cd_spend.filter())
async def purchase_confirmation(call, callback_data: dict):
    cur_text = f"Вы точно хотите купить <b>{callback_data['title']}</b>?"
    await main_edit_mes(text=cur_text,
                        ikb=keyboard.get_confirmation(callback_data['id'], callback_data['title'], callback_data['cost']),
                        call=call)


# Purchase end and back to spend menu
@dp.callback_query_handler(IsStudent(), keyboard.cd_purchase.filter())
async def purchse_end(call, callback_data):
    cost, title = int(callback_data['cost']), callback_data['title']
    std_id, score, name = main_get(tables=['students'], columns=['id', 'score', "name"],
                                   condition=f'tg_id = {call.message.chat.id}', is_one=True)
    if int(score) >= cost:
        update_record(table='students', rec_id=std_id, columns={'score': score - int(cost)})
        text_admin = text['log_spend'].format(std=name, cost=cost, award=title, date=date.today())
        await bot.send_message(text=text_admin, chat_id="-1001881010069", parse_mode='html')
        await call.answer('Покупка прошла успешно')
        await main_edit_mes(text=random.choice(text['spend']), ikb=keyboard.get_records_list('awards'), call=call)
    else:
        await call.answer('Недостаточно средств')