from aiogram import Dispatcher
from .is_admin import IsAdmin
from .is_student import IsStudent
from .is_developer import IsDeveloper
from .is_teacher import IsTeacher

def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsDeveloper, event_handlers=[dp.message_handlers])
    dp.filters_factory.bind(IsAdmin, event_handlers=[dp.message_handlers])
    dp.filters_factory.bind(IsStudent, event_handlers=[dp.message_handlers])
    dp.filters_factory.bind(IsTeacher, event_handlers=[dp.message_handlers])