from aiogram.dispatcher.filters.state import StatesGroup, State


class FinalStates(StatesGroup):
    doc = State()
    receipt = State()
