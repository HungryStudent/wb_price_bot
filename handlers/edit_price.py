from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

import keyboards.user as user_kb
from states.user import ChangePrice

from create_bot import dp
from core import crud, schemas, wb_api


@dp.callback_query_handler(text="edit_price", state="*")
async def show_account_for_edit_price(call: CallbackQuery, state: FSMContext):
    await state.finish()
    accounts = crud.get_accounts(call.from_user.id)
    if accounts is None:
        await call.message.edit_text("""<b>Пока что не подключен ни один аккаунт</b>

Перейдите в настройки для подключения аккаунта""", reply_markup=user_kb.setting_and_menu)
    else:
        await call.message.edit_text("""<b>Выберите аккаунт</b>

🟢 API ключ подключен
🔴 API НЕ ключ подключен""", reply_markup=user_kb.get_accounts_for_edit_price(accounts))


@dp.callback_query_handler(Text(startswith="edit_price_by_account"))
async def start_edit_price_by_account(call: CallbackQuery, state: FSMContext):
    account_id = call.data.split(":")[1]
    account = crud.get_account(account_id)
    if account.api_key is None:
        await call.message.edit_text("<b>Подключите API ключ в настройках</b>", reply_markup=user_kb.back_to_menu)
        return
    is_api_key_valid = await wb_api.check_api_token(account.api_key)
    if not is_api_key_valid:
        await call.message.edit_text("<b>Неверный API ключ, измените его в настройках</b>", reply_markup=user_kb.back_to_menu)
    else:
        await call.message.edit_text("<b>Введите артикул товара для изменения цены</b>",
                                     reply_markup=user_kb.back_to_edit_price)
        await state.set_state(ChangePrice.article)
        await state.update_data(account_id=account_id)


@dp.message_handler(state=ChangePrice.article)
async def enter_article(message: Message, state: FSMContext):
    try:
        article = int(message.text)
    except ValueError:
        await message.answer("<b>Артикул не найден.</b>", reply_markup=user_kb.try_again_enter_article)
        return
    card: schemas.CardOut = await wb_api.get_card(article)
    if card is None:
        await message.answer("<b>Артикул не найден.</b>", reply_markup=user_kb.try_again_enter_article)
    else:
        await message.answer(f"""Артикул: <u>{card.id}</u>
<b>Сейчас</b>
Цена ДО скидки: {card.priceU // 100}р
Размер скидки: {card.sale}%

Цена: <b>{card.salePriceU // 100}р</b> (без СПП)

Какую цену установить?
(напишите просто число)""", reply_markup=user_kb.back_to_edit_price)
        await state.update_data(article=article, card=card)
        await state.set_state(ChangePrice.new_price)


@dp.message_handler(state=ChangePrice.new_price)
async def enter_new_price(message: Message, state: FSMContext):
    try:
        new_price = int(message.text)
    except ValueError:
        await message.answer("Введите целое число!")
        return
    await state.update_data(new_price=new_price)
    data = await state.get_data()
    await message.answer(f"""Артикул: <u>{data['article']}</u>

Устанавливаем цену <b>{new_price}</b>

Меняем через <b>цену до скидки</b> или <b>размер скидки</b>?""", reply_markup=user_kb.price_change_type)


@dp.callback_query_handler(Text(startswith="pre_change_price"), state=ChangePrice.new_price)
async def pre_change_pre_price(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    card: schemas.CardOut = data["card"]
    article = data["article"]
    new_price = data["new_price"]

    change_price_type = call.data.split(":")[1]
    await state.update_data(change_price_type=change_price_type)
    if change_price_type == "pre_price":
        change_price = int(new_price / (1 - 0.01 * card.sale))
        finish_new_price = int(change_price * (1 - card.sale * 0.01))
        await call.message.edit_text(f"""Артикул: <u>{card.id}</u>
    
Цена ДО скидки: <b><del>{card.priceU // 100} руб</del> {change_price} руб</b>
Размер скидки: {card.sale}%
    
🆕 <b>Новая цена: {finish_new_price} руб</b>""", reply_markup=user_kb.approve_change_price)
        await state.update_data(change_price=change_price)

    elif change_price_type == "sale":
        change_sale = int((card.priceU // 100 - new_price) * 100 / (card.priceU // 100))
        finish_new_price = int((card.priceU // 100) * (1 - change_sale * 0.01))
        await call.message.edit_text(f"""Артикул: <u>{card.id}</u>

Размер скидки: <b><del>{card.sale}%</del> {change_sale}%</b>
Цена ДО скидки: {card.priceU // 100}

🆕 <b>Новая цена: {finish_new_price} руб</b>""",
                                     reply_markup=user_kb.approve_change_price)
        await state.update_data(change_sale=change_sale)
    await state.update_data(finish_new_price=finish_new_price)


@dp.callback_query_handler(text="try_again_enter_article", state=ChangePrice.article)
async def try_again_enter_article(call: CallbackQuery):
    await call.message.edit_text("<b>Введите артикул товара для изменения цены</b>",
                                 reply_markup=user_kb.back_to_edit_price)


@dp.callback_query_handler(text="back_to_enter_price_for_change_article", state=ChangePrice.new_price)
async def back_to_enter_price_for_change_article(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    card: schemas.CardOut = data["card"]
    await call.message.edit_text(f"""Артикул: <u>{card.id}</u>
<b>Сейчас</b>
Цена ДО скидки: {card.priceU // 100}р
Размер скидки: {card.sale}%

Цена: <b>{card.salePriceU // 100}р</b> (без СПП)

Какую цену установить?
(напишите просто число)""", reply_markup=user_kb.back_to_edit_price)


@dp.callback_query_handler(text="back_to_price_change_type", state=ChangePrice.new_price)
async def back_to_price_change_type(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(f"""Артикул: <u>{data['article']}</u>

Устанавливаем цену <b>{data['new_price']}</b>

Меняем через <b>цену до скидки</b> или <b>размер скидки</b>?""", reply_markup=user_kb.price_change_type)


@dp.callback_query_handler(text="approve_change_price", state=ChangePrice.new_price)
async def approve_change_price(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    account = crud.get_account(data["account_id"])
    if data["change_price_type"] == "pre_price":
        res = await wb_api.change_price_by_pre_price(schemas.ChangePriceByPrePrice(api_key=account.api_key,
                                                                                   article=data["article"],
                                                                                   price=data["change_price"]))
    elif data["change_price_type"] == "sale":
        res = await wb_api.change_price_by_sale(schemas.ChangePriceBySale(api_key=account.api_key,
                                                                          article=data["article"],
                                                                          discount=data["change_sale"]))
    if res == "Error":
        await call.message.answer("Произошла ошибка, повторите попытку позже", reply_markup=user_kb.back_to_menu)
        await state.finish()
        return

    await call.message.edit_text(f"""✅ <b>ЦЕНА УСПЕШНО ИЗМЕНЕНА</b>

Артикул: {data['article']}
Новая цена: <b>{data['finish_new_price']} руб</b>

Цены обновятся на Wildberries в течение <b>3-5 мин.</b>""", reply_markup=user_kb.finish_change_price)
