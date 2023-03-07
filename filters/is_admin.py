from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from func_bot import main_get, update_record


class IsAdmin(BoundFilter):

    async def check(self, message: Message):
        admins_tg_id = main_get(tables=["admins"], columns=["tg_id"])
        cur_id = message.from_user.id
        cur_name = message.from_user.username
        if cur_id in admins_tg_id:
            return True
        return False
