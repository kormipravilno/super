from aiogram.dispatcher.filters.state import StatesGroup, State


class HasStateStartStates(StatesGroup):
    confirm = State()
