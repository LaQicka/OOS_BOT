from aiogram.fsm.state import StatesGroup, State

class UserState(StatesGroup):
    notif_not_set = State()
    wait_for_day = State()
    wait_for_hour = State()
    notif_set = State()

