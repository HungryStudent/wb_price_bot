from aiogram.types import CallbackQuery
import keyboards.user as user_kb
from config import BOT_NAME, SUPPORT_NAME
from create_bot import dp
from core import crud


@dp.callback_query_handler(text="ref_system")
async def show_ref_stat(call: CallbackQuery):
    ref_stat = crud.get_ref_stat(call.from_user.id)
    await call.message.edit_text(f"""<b>Рассказывай друзьям о нашем боте и получай 20% от каждой оплаты реферала.</b>

Реферальная ссылка: <code>https://t.me/{BOT_NAME}/start={call.from_user.id}</code>

Рефералов: {ref_stat.ref_count}
Баланс: {ref_stat.balance} руб.""", reply_markup=user_kb.ref_menu)


@dp.callback_query_handler(text="ref_balance_to_account")
async def ref_balance_to_account(call: CallbackQuery):
    ref_stat = crud.get_ref_stat(call.from_user.id)
    if ref_stat.balance > 0:
        new_balance = crud.ref_balance_to_account(call.from_user.id)
        await call.message.edit_text(f"""{ref_stat.balance}₽ - зачислена на баланс бота
Баланс бота: {new_balance}₽""", reply_markup=user_kb.back_to_menu)
    else:
        await call.message.edit_text(f"""Ваш баланс пока что <b>0₽</b>, рекомендуйте нашего бота и получайте 20% от каждой оплаты вашего реферала.

Ваша реферальная ссылка: <code>https://t.me/{BOT_NAME}/start={call.from_user.id}</code>""",
                                     reply_markup=user_kb.back_to_menu)


@dp.callback_query_handler(text="withdraw_ref_balance")
async def withdraw_ref_balance(call: CallbackQuery):
    ref_stat = crud.get_ref_stat(call.from_user.id)
    if ref_stat.balance > 0:
        await call.message.edit_text(f'Для вывода партнерского вознаграждения напишите нам @{SUPPORT_NAME}',
                                     reply_markup=user_kb.back_to_menu)
    else:
        await call.message.edit_text(f"""Ваш баланс пока что <b>0₽</b>, рекомендуйте нашего бота и получайте 20% от каждой оплаты вашего реферала.

Ваша реферальная ссылка: <code>https://t.me/{BOT_NAME}/start={call.from_user.id}</code>""",
                                     reply_markup=user_kb.back_to_menu)
