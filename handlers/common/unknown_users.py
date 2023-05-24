from create_bot import bot, dp
from script_text.common import text
from func_bot import *


@dp.message_handler(commands=['start'])
async def start_handler(message):
    admins_usernames = ['@' + name for name in main_get(tables=['admins'], columns=['tg_username'])]
    await bot.send_message(message.from_user.id, text['start'].format('\n'.join(admins_usernames)), parse_mode='html')
