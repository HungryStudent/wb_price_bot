from aiogram.dispatcher.filters.state import StatesGroup, State





class CreateAccount(StatesGroup):
    key = State()
    name = State()


class EditAccount(StatesGroup):
    value = State()


class AddApiKey(StatesGroup):
    api_key = State()


class ChangePrice(StatesGroup):
    article = State()
    new_price = State()


class EditMonitoring(StatesGroup):
    article = State()
    price = State()


class FindMonitoringArticle(StatesGroup):
    article = State()


class ExcelEditMonitoring(StatesGroup):
    file = State()


class TopUpBalance(StatesGroup):
    amount = State()