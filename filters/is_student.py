from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from func_bot import main_get, update_record


class IsStudent(BoundFilter):
    async def check(self, message: Message):
        students_tg_id, students_usernames, students_id = main_get(tables=["students"], columns=["tg_id", "tg_username", "id"])
        cur_id = message.from_user.id
        cur_name = message.from_user.username
        if cur_id in students_tg_id:
            return True
        if cur_name in students_usernames:
            index = students_usernames.index(cur_name)
            update_record(table="students", rec_id=students_id[index], columns={"tg_id": cur_id})
            return True
        return False