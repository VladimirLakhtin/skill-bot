from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter
from config import DEVELOPERS

class IsDeveloper(BoundFilter):
    async def check(self, message: Message):
        return message.from_user.id in DEVELOPERS

