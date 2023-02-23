import data_checking
import keyboards.student_keyboards as keyboard
from create_bot import bot, dp
import func_bot

async def main_edit_mes(text, ikb, call=None, message_id=None, chat_id=None):
    if message_id == None and call != None:
        message_id = call.message.message_id
    if chat_id == None and call != None:
        chat_id = call.message.chat.id
    await bot.edit_message_text(
        text=text,
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=ikb)
    

#------------------------------------------------Main------------------------------------------------

# Main menu
@dp.message_handler(commands=['start'])
async def start_handler(message):
    await bot.send_message(message.from_user.id, f"Добро пожаловать в главное меню, {message.from_user.first_name}", reply_markup=keyboard.get_main_menu())


# Back to main menu
@dp.callback_query_handler(keyboard.cd_main_menu.filter(chapter='menu'))
async def back_main_menu(call):
    text = f"Добро пожаловать в главное меню {call.message.from_user.first_name}"
    await main_edit_mes(text=text, ikb=keyboard.get_main_menu(), call=call)


#-----------------------------------------------Cheak-----------------------------------------------

# Cheak SkillCoins account
@dp.callback_query_handler(keyboard.cd_main_menu.filter(chapter='cheak'))
async def cheak_account(call):
    print(call.message.chat.id)
    score = func_bot.main_get(tables=['students'], columns=['score'], condition=f'tg_id = {call.message.chat.id}')[0]
    await main_edit_mes(text=f'Твой счёт: {score}', ikb=keyboard.get_back(), call=call)


#------------------------------------------------Earn------------------------------------------------

# Ways to earn SkillCoins list
@dp.callback_query_handler(keyboard.cd_main_menu.filter(chapter='earn'))
async def ways_to_earn(call):
    text = 'Ways to earn'
    await main_edit_mes(text=text, ikb=keyboard.get_back(), call=call)


#-----------------------------------------------Incomes-----------------------------------------------

# Ways to spend SkillCoins list
@dp.callback_query_handler(keyboard.cd_main_menu.filter(chapter='spend'))
async def ways_to_spend(call):
    text = 'Spend, please ->'
    await main_edit_mes(text=text, ikb=keyboard.get_list_spend(), call=call)


# Accept or reject purchase
@dp.callback_query_handler(keyboard.cd_spend.filter())
async def purchase_confirmation(call, callback_data: dict):
    score = func_bot.main_get(tables=['students'], columns=['score'], condition=f'tg_id = {call.message.chat.id}')[0]
    if score >= int(callback_data['cost']):
        text = 'Yes or not'
        await main_edit_mes(text=text, ikb=keyboard.get_confirmation(callback_data['id'], callback_data['title'], callback_data['cost']), call=call)
    else:
        await call.answer('Недостаточно средств')


# Purchase end and back to spend menu
@dp.callback_query_handler(keyboard.cd_purchase.filter())
async def purchse_end(call, callback_data):
    std_id, score = func_bot.main_get(tables=['students'], columns=['id', 'score'], condition=f'tg_id = {call.message.chat.id}')
    func_bot.update_record(table='students', rec_id=std_id[0], columns={'score': score[0] - int(callback_data['cost'])})
    text = f'Purchase is done: {callback_data["title"]}\nSpend, please ->'
    await main_edit_mes(text=text, ikb=keyboard.get_list_spend(), call=call)