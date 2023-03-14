from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMAddRecord(StatesGroup):
    state_name = State()
    state_yes_and_no = State()
    state_prof = State()
    state_tg_name = State()

    state_title = State()
    state_info_title = State()
    state_cost = State()

    accept_or_reject = State()


class FSMEditFeat(StatesGroup):
    edit_records_state = State()


class FSMSeachRecord(StatesGroup):
    search_name_state = State()


class FSMSeachStudent(StatesGroup):
    search_name_state = State()


class FSMDeveloper(StatesGroup):
    add_name_admin_state = State()
    add_id_admin_state = State()
    accept_or_reject_admin_state = State()
    edit_admin_state = State()


class FSMTeachers(StatesGroup):
    add_day_state = State()
    add_coins_state = State()