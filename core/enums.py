from enum import Enum


class AccountTypes(Enum):
    automate = 1
    half_automate = 2
    notify = 3


class SubTypes(Enum):
    days = 1
    forever = 2

class ProductTypes(Enum):
    balance = 1
    forever = 2

account_type_text = {AccountTypes.automate.value: "🟢 ",
                     AccountTypes.half_automate.value: "🟡 ",
                     AccountTypes.notify.value: "🔴 "}