from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions, ChatMember, LabeledPrice, PreCheckoutQuery

import keyboards.admin as admin_kb
import keyboards.user as user_kb
from states.user import ExcelEditMonitoring, TopUpBalance
from config import ADMINS, video_1, video_2, pay_token
from create_bot import dp
from core import crud, schemas, wb_api, excel_api
from core.enums import AccountTypes, ProductTypes
import os


@dp.callback_query_handler(text="top_up_balance")
async def top_up_balance(call: CallbackQuery):
    await call.message.edit_text("Введите сумму пополнения баланса (минимум 290₽)",
                                 reply_markup=user_kb.back_to_personal_account)
    await TopUpBalance.amount.set()


@dp.callback_query_handler(text="buy_forever_menu")
async def buy_forever_menu(call: CallbackQuery):
    accounts = crud.get_accounts_for_buy_forever(call.from_user.id)

    await call.message.edit_text("""Выберите аккаунт

Стоимость тарифа: 
9900₽ за первый аккаунт
4900₽ за каждый следующий

Подключено может быть любое количество аккаунтов""", reply_markup=user_kb.get_accounts_for_buy_forever(accounts))


@dp.callback_query_handler(Text(startswith="buy_forever:"))
async def issue_an_invoice_for_forever(call: CallbackQuery):
    account_id = call.data.split(":")[1]
    user = crud.get_user(call.from_user.id)
    if user.is_buy_forever:
        amount = 4900
    else:
        amount = 9900
    order_id = crud.create_order(
        schemas.OrderCreate(user_id=call.from_user.id, product_type=ProductTypes.forever.value, amount=amount,
                            account_id=account_id))
    await call.bot.send_invoice(call.from_user.id, title="Оплата аккаунта",
                                description="Для оплаты тарифа перейдите по ссылке: Оплатить",
                                payload=order_id, provider_token=pay_token, currency="RUB",
                                prices=[LabeledPrice(label="Оплата аккаунта", amount=amount * 100)],
                                reply_markup=user_kb.back_to_menu_from_pay)
    await call.message.delete()


@dp.message_handler(state=TopUpBalance.amount)
async def issue_an_invoice_for_balance(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Введите целое число!")
        return
    if amount < 290:
        await message.answer("Минимальная сумма пополнения 290 рублей")
        return
    order_id = crud.create_order(
        schemas.OrderCreate(user_id=message.from_user.id, product_type=ProductTypes.balance.value, amount=amount))
    await message.bot.send_invoice(message.from_user.id, title="Пополнение баланса",
                                   description="Для оплаты тарифа перейдите по ссылке: Оплатить",
                                   payload=order_id, provider_token=pay_token, currency="RUB",
                                   prices=[LabeledPrice(label="Пополнение баланса", amount=amount * 100)],
                                   reply_markup=user_kb.back_to_menu_from_pay)
    await state.finish()


@dp.pre_checkout_query_handler()
async def approve_order(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types="successful_payment")
async def process_successful_payment(message: Message):
    order = crud.get_order(message.successful_payment.invoice_payload)
    crud.set_order_is_payd(order.id)
    user = crud.get_user(order.user_id)
    crud.add_ref_balance(user.inviter_id, amount=int(order.amount * 0.02))
    if order.product_type == ProductTypes.balance.value:
        crud.add_balance(order.user_id, order.amount)
        await message.answer(f"Баланс успешно пополнен на {order.amount} руб.")
    elif order.product_type == ProductTypes.forever.value:
        crud.activate_account(order.account_id, order.user_id)
        await message.answer("Аккаунт активирован навсегда!")
