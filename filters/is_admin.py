from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from func_bot import main_get, update_record



class IsAdmin(BoundFilter):

    async def check(self, message: Message):
        admins_tg_id = main_get(tables=["admins"], columns=["tg_id"])
        teachers_tg_id, teachers_usernames, teachers_id = main_get(tables=["teachers"], columns=["tg_id", "tg_username", "id"])
        cur_id = message.from_user.id
        cur_name = message.from_user.username
        if cur_id in admins_tg_id or cur_id in teachers_tg_id:
            return True
        if cur_name in teachers_usernames:
            index = teachers_usernames.index(cur_name)
            update_record(table="teachers", rec_id=teachers_id[index], columns={"tg_id": cur_id})
            return True
        return False
