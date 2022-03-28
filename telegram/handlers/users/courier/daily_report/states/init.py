from aiogram.dispatcher.filters.state import StatesGroup, State


class InitStates(StatesGroup):
    mileage = State()
    odometer = State()
