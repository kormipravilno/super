from aiogram.dispatcher.filters.state import StatesGroup, State


class FinalStates(StatesGroup):
    shift_opened = State()
    confirm = State()
    orders = State()
    orders_noreceipt = State()
    mileage_final = State()
    proceeds = State()
    proceeds_cash = State()
    cash_noreceipt = State()
    cash_atm = State()
    atm_receipt = State()
    cardtocard_receipt = State()
    close_shift = State()
