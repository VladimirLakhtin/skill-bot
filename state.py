from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAdmin(StatesGroup):

    state_name = State()
    state_yes_and_no = State()
    state_prof = State()
    state_tg_name = State()
    accept_or_reject = State()

    state_add_profession = State()

    search_name_state = State()

    edit_records_state = State()
