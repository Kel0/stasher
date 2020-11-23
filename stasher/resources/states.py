from aiogram.dispatcher.filters.state import State, StatesGroup


class BankState(StatesGroup):
    bank = State()


class CostsCategoryState(StatesGroup):
    name = State()


class CostState(StatesGroup):
    category = State()
    name = State()
    price = State()
    location = State()
