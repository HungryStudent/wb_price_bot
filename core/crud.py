from typing import List

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from core import models, schemas
from core.database import SessionLocal
from core.enums import SubTypes


def get_db():
    db = SessionLocal()
    return db


def add_user(user_data: schemas.UserCreate):
    db: Session = get_db()
    user = models.Users(**user_data.dict())
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        pass


def get_users() -> List[schemas.UserOut]:
    db: Session = get_db()
    return db.query(models.Users).all()


def get_user(user_id):
    db: Session = get_db()
    res = db.query(models.Users.user_id, models.Users.inviter_id, models.Users.is_buy_forever,
                   models.Users.balance.label("balance"),
                   func.count(models.Accounts.id).filter(models.Accounts.account_type == SubTypes.days.value).label(
                       "days_count"),
                   func.count(models.Accounts.id).filter(models.Accounts.account_type == SubTypes.forever.value).label(
                       "forever_count")).join(
        models.Accounts, models.Accounts.user_id == models.Users.user_id, isouter=True).filter(
        models.Users.user_id == user_id).group_by(models.Users.user_id).first()
    return schemas.UserOut(user_id=res.user_id, balance=res.balance, days_count=res.days_count,
                           forever_count=res.forever_count, is_buy_forever=res.is_buy_forever,
                           inviter_id=res.inviter_id)


def get_ref_stat(user_id) -> schemas.RefStatOut:
    db: Session = get_db()
    return db.query(models.Users.ref_balance.label("balance"),
                    func.count(models.Users.inviter_id).filter(models.Users.inviter_id == user_id).label(
                        "ref_count")).filter(models.Users.user_id == user_id).group_by(models.Users.user_id).first()


def ref_balance_to_account(user_id):
    db: Session = get_db()
    db.query(models.Users).filter(models.Users.user_id == user_id).update(
        {"balance": models.Users.balance + models.Users.ref_balance,
         "ref_balance": 0})
    db.commit()
    return db.query(models.Users.balance).filter(models.Users.user_id == user_id).first()[0]


def add_ref_balance(user_id, amount):
    db: Session = get_db()
    db.query(models.Users).filter(models.Users.user_id == user_id).update(
        {"ref_balance": models.Users.balance + amount})
    db.commit()


def add_balance(user_id, amount):
    db: Session = get_db()
    db.query(models.Users).filter(models.Users.user_id == user_id).update(
        {"balance": models.Users.balance + amount})
    db.commit()


def add_account(account_data: schemas.AccountCreate):
    db: Session = get_db()
    account = models.Accounts(**account_data.dict())

    try:
        db.add(account)
        db.commit()
    except IntegrityError:
        return "IntegrityError"


def get_accounts(user_id) -> List[schemas.AccountOut]:
    db: Session = get_db()
    return db.query(models.Accounts).filter(models.Accounts.user_id == user_id).all()


def get_account(account_id) -> schemas.AccountOut:
    db: Session = get_db()
    return db.query(models.Accounts).filter(models.Accounts.id == account_id).first()


def edit_account(edit_data: schemas.AccountEdit):
    db: Session = get_db()
    db.query(models.Accounts).filter(models.Accounts.id == edit_data.account_id).update(
        {edit_data.field: edit_data.value})
    db.commit()


def activate_account(account_id, user_id):
    db: Session = get_db()
    db.query(models.Accounts).filter(models.Accounts.id == account_id).update(
        {"sub_type": SubTypes.forever.value})
    db.query(models.Users).filter(models.Users.user_id == user_id).update(
        {"is_buy_forever": True})
    db.commit()


def delete_account(account_id):
    db: Session = get_db()
    db.query(models.Accounts).filter(models.Accounts.id == account_id).delete()
    db.commit()


def get_article(article_id) -> schemas.ArticleOut:
    db: Session = get_db()
    return db.query(models.Articles).filter(models.Articles.id == article_id).first()


def get_article_by_id_an_account_id(article_id, account_id) -> schemas.ArticleOut:
    db: Session = get_db()
    return db.query(models.Articles).filter(models.Articles.id == article_id,
                                            models.Articles.account_id == account_id).first()


def get_articles_by_account_id(account_id, page) -> List[schemas.ArticleOut]:
    db: Session = get_db()
    return db.query(models.Articles).filter(models.Articles.account_id == account_id).order_by(
        models.Articles.id).limit(
        10).offset(page * 10 - 10).all()


def get_full_articles_by_account_id(account_id) -> List[schemas.ArticleOut]:
    db: Session = get_db()
    return db.query(models.Articles).filter(models.Articles.account_id == account_id).all()


def get_articles_count_by_account_id(account_id):
    db: Session = get_db()
    return db.query(func.count(models.Articles.id)).filter(models.Articles.account_id == account_id).first()


def add_article(article_data: schemas.ArticleCreate):
    db: Session = get_db()
    article = models.Articles(**article_data.dict())
    db.add(article)
    db.commit()


def change_price_on_article(edit_data: schemas.ArticleEdit):
    db: Session = get_db()
    db.query(models.Articles).filter(models.Articles.id == edit_data.id).update(
        {"min_price": edit_data.min_price})
    db.commit()


def changes_articles_by_account_id(account_id, articles: list[schemas.ArticleEdit]):
    db: Session = get_db()
    for article in articles:
        curr_article = db.query(models.Articles).filter(models.Articles.account_id == account_id,
                                                        models.Articles.id == article.id).first()
        if curr_article:
            db.query(models.Articles).filter(models.Articles.id == article.id).update(
                {"min_price": article.min_price})
        else:
            article = models.Articles(id=article.id, min_price=article.min_price, account_id=account_id)
            db.add(article)
            try:
                db.commit()
            except IntegrityError:
                pass


def get_accounts_with_days_sub(user_id) -> List[schemas.AccountOut]:
    db: Session = get_db()
    db.query(models.Accounts).filter(models.Accounts.user_id == user_id).update(
        {"is_payd": False})
    db.commit()
    return db.query(models.Accounts).filter(models.Accounts.user_id == user_id,
                                            models.Accounts.sub_type == SubTypes.days.value).all()


def get_accounts_for_buy_forever(user_id) -> List[schemas.AccountOut]:
    db: Session = get_db()
    return db.query(models.Accounts).filter(models.Accounts.user_id == user_id,
                                            models.Accounts.sub_type == SubTypes.days.value).all()


def get_accounts_with_payd_days_sub() -> List[schemas.AccountOut]:
    db: Session = get_db()
    return db.query(models.Accounts).filter(models.Accounts.is_payd == True,
                                            models.Accounts.sub_type == SubTypes.days.value).all()


def get_accounts_with_payd_forever_sub() -> List[schemas.AccountOut]:
    db: Session = get_db()
    return db.query(models.Accounts).filter(models.Accounts.sub_type == SubTypes.forever.value).all()


def set_account_is_payd(account_id, user_id):
    db: Session = get_db()
    db.query(models.Accounts).filter(models.Accounts.id == account_id).update(
        {"is_payd": True})
    db.query(models.Users).filter(models.Users.user_id == user_id).update(
        {"balance": models.Users.balance - 16})
    db.commit()


def create_order(order_data: schemas.OrderCreate):
    db: Session = get_db()
    order = models.Orders(**order_data.dict())
    db.add(order)
    db.flush()
    order_id = order.id
    db.commit()
    return order_id


def get_order(order_id) -> schemas.OrderOut:
    db: Session = get_db()
    return db.query(models.Orders).filter(models.Orders.id == order_id).first()


def set_order_is_payd(order_id):
    db: Session = get_db()
    db.query(models.Orders).filter(models.Orders.id == order_id).update(
        {"is_payd": True})
    db.commit()
