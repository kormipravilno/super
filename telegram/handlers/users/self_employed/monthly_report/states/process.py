from aiogram.dispatcher.filters.state import StatesGroup, State


class ProcessStates(StatesGroup):
    selection = State()
    value = State()
    photo = State()
    is_okay = State()
