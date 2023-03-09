from create_bot import bot, dp
from filters import IsDeveloper


@dp.callback_query_handler(IsDeveloper(), lambda callback: callback.data == 'get_file_db')
async def get_db_file(call):
    with open("db.db", "rb") as file:
        path = file.read()
    await bot.send_document(call.message.chat.id, ('db.dp', path))
