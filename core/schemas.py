from typing import Union
from datetime import datetime

from pydantic import BaseModel

from core.enums import SubTypes


class OrderCreate(BaseModel):
    user_id: int
    product_type: int
    account_id: int = None
    amount: int = None
    is_payd: bool = False


class OrderOut(BaseModel):
    id: int
    user_id: int
    product_type: int
    account_id: int = None
    amount: int = None
    is_payd: bool = False


class UserCreate(BaseModel):
    user_id: int
    username: str
    reg_time: datetime
    balance: int = 224
    ref_balance: int = 0
    inviter_id: int
    is_buy_forever: bool = False


class UserOut(BaseModel):
    user_id: int
    balance: int
    days_count: int
    forever_count: int
    is_buy_forever: bool
    inviter_id: int


class AccountCreate(BaseModel):
    user_id: int
    name: str
    account_type: int
    api_key: str = None
    seller_id: int = None
    sub_type: int = SubTypes.days.value
    is_payd: bool = False


class AccountOut(BaseModel):
    id: int
    user_id: int
    name: str
    account_type: int
    api_key: str = None
    seller_id: int = None


class AccountEdit(BaseModel):
    account_id: int
    field: str
    value: Union[str, int]


class CardOut(BaseModel):
    id: int
    priceU: int
    salePriceU: int
    sale: int
    name: str
    brand: str


class ChangePriceBySale(BaseModel):
    api_key: str
    article: int
    discount: int


class MassChangePrice(BaseModel):
    nm: int
    price: int


class ChangePriceByPrePrice(BaseModel):
    api_key: str
    article: int
    price: int


class RefStatOut(BaseModel):
    balance: int
    ref_count: int


class ArticleCreate(BaseModel):
    id: int
    account_id: int
    min_price: int


class ArticleOut(BaseModel):
    id: int
    account_id: int
    min_price: int


class ArticleEdit(BaseModel):
    id: int
    min_price: int
