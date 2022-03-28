from aiogram.dispatcher.filters.state import StatesGroup, State


class ClearStateStates(StatesGroup):
    user_id = State()
