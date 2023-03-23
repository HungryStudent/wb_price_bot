from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, VARCHAR, TIMESTAMP, SMALLINT

from .database import Base


class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(VARCHAR(32))
    reg_time = Column(TIMESTAMP)
    balance = Column(Integer)
    ref_balance = Column(Integer)
    inviter_id = Column(BigInteger)
    is_buy_forever = Column(Boolean)


class Accounts(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey(Users.user_id))
    name = Column(VARCHAR(256))
    account_type = Column(SMALLINT)
    api_key = Column(VARCHAR(256), unique=True)
    seller_id = Column(Integer, unique=True)
    sub_type = Column(SMALLINT)
    is_payd = Column(Boolean)


class Articles(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey(Accounts.id))
    min_price = Column(Integer)


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey(Users.user_id))
    product_type = Column(SMALLINT)
    account_id = Column(Integer, ForeignKey(Accounts.id))
    amount = Column(Integer)
    is_payd = Column(Boolean)
