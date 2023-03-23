from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions, ChatMember
from aiogram.utils.exceptions import BadRequest

import keyboards.admin as admin_kb
import keyboards.user as user_kb
from states.user import CreateAccount, EditAccount, AddApiKey, ChangePrice, EditMonitoring
from config import ADMINS, video_1, video_2
from create_bot import dp
from core import crud, schemas, wb_api
from core.enums import AccountTypes


@dp.callback_query_handler(text="monitoring_menu", state="*")
async def monitoring_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    accounts = crud.get_accounts(call.from_user.id)
    await call.message.edit_text("""<b>Если цена станет меньше минимальной:</b>
🟢 Бот поднимет цену (API ключ подключен)
🟡 Бот запросит подтверждение изменения цены 
⚪ Бот пришлет уведомление (API НЕ ключ подключен)""", reply_markup=user_kb.get_accounts_for_monitoring(accounts))


@dp.callback_query_handler(Text(startswith="monitoring_by_account"))
async def account_monitoring_menu(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    try:
        await call.message.edit_text("<b>Выберите пункт меню</b>", reply_markup=user_kb.get_monitoring_menu(account_id))
    except BadRequest:
        await call.message.answer("<b>Выберите пункт меню</b>", reply_markup=user_kb.get_monitoring_menu(account_id))
        await call.answer()


@dp.callback_query_handler(Text(startswith="edit_monitoring_account"))
async def edit_account_monitoring(call: CallbackQuery, state: FSMContext):
    account_id = call.data.split(":")[1]
    await call.message.edit_text("<b>Введите артикул товара для создания / изменения мониторинга</b>",
                                 reply_markup=user_kb.get_edit_account_monitoring(account_id))
    await EditMonitoring.article.set()
    await state.update_data(account_id=account_id)


@dp.message_handler(state=EditMonitoring.article)
async def enter_article_for_add_to_monitoring(message: Message, state: FSMContext):
    try:
        article_id = int(message.text)
    except ValueError:
        await message.answer("Введите число!")
        return
    data = await state.get_data()
    account = crud.get_account(data["account_id"])

    if not await wb_api.get_card(article_id):
        await message.answer("Артикул не найден")
        return
    if account.account_type != AccountTypes.notify.value:
        if not await wb_api.is_my_card(account.api_key, article_id):
            await message.answer("Данный артикул не принадлежит этому аккаунту")
            return

    article = crud.get_article(article_id)
    card: schemas.CardOut = await wb_api.get_card(article_id)
    await state.update_data(article_id=article_id, have_article=bool(article))
    if article:
        await message.answer(f"""Артикул: <u>{card.id}</u>
<b>Сейчас</b>
Цена ДО скидки: {card.priceU // 100}р
Размер скидки: {card.sale}%

Цена: <b>{card.salePriceU // 100}р</b> (без СПП)
Мин. цена: <b>{article.min_price}р</b>

Укажите новую минимальную цену, ниже которой товар не должен опускаться?""",
                             reply_markup=user_kb.get_article_for_monitoring(article_id))
    else:
        await message.answer(f"""Артикул: <u>{card.id}</u>
<b>Сейчас</b>
Цена ДО скидки: {card.priceU // 100}р
Размер скидки: {card.sale}%

Цена: <b>{card.salePriceU // 100}р</b>

Укажите минимальную цену, ниже которой товар не должен опускаться?""",
                             reply_markup=user_kb.get_article_for_monitoring(article_id))
    await EditMonitoring.price.set()


@dp.message_handler(state=EditMonitoring.price)
async def update_price(message: Message, state: FSMContext):
    try:
        min_price = int(message.text)
    except ValueError:
        await message.answer("Введите пожалуйста целое число")
        return
    data = await state.get_data()
    if data["have_article"]:
        crud.change_price_on_article(schemas.ArticleEdit(id=data["article_id"], min_price=min_price))
    else:
        crud.add_article(
            schemas.ArticleCreate(id=data["article_id"], account_id=data["account_id"], min_price=min_price))
    await message.answer(f"""✅ <b>УСПЕШНО УСТАНОВЛЕНО</b>
    
Артикул: <u>{data['article_id']}</u>
Мин. цена: <b>{min_price} руб</b>""", reply_markup=user_kb.get_finish_change_monitoring_price(data["account_id"]))
    await state.finish()
