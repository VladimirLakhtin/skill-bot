from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAdmin(StatesGroup):

    state_add_name = State()
    state_yes_and_no = State()
    state_add_type = State()
    state_add_tg_name = State()
    accept_or_reject = State()

    state_add_profession = State()
    accept_or_reject_type = State()

    search_name_state = State()
