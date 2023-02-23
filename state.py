from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class FSMAddRecord(StatesGroup):
    state_name = State()
    state_yes_and_no = State()
    state_prof = State()
    state_tg_name = State()

    state_title = State()
    state_cost = State()

    accept_or_reject = State()


class FSMEditFeat(StatesGroup):
    edit_records_state = State()


class FSMSeachRecord(StatesGroup):
    search_name_state = State()

