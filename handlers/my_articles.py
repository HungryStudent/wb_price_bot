import os

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions, ChatMember

import keyboards.admin as admin_kb
import keyboards.user as user_kb
from states.user import CreateAccount, EditAccount, AddApiKey, ChangePrice, EditMonitoring, FindMonitoringArticle
from config import ADMINS, video_1, video_2
from create_bot import dp
from core import crud, schemas, wb_api, excel_api
from core.enums import AccountTypes

num_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


@dp.callback_query_handler(Text(startswith="my_monitoring_articles_menu"))
async def my_monitoring_articles_menu(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    await call.message.edit_text("<b>Отслеживания</b>",
                                 reply_markup=user_kb.get_my_monitoring_articles_menu(account_id))


@dp.callback_query_handler(Text(startswith="my_monitoring_articles"))
async def my_monitoring_articles(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    page = int(call.data.split(":")[2])
    articles_count = crud.get_articles_count_by_account_id(account_id)[0]
    max_page = articles_count // 10
    if articles_count % 10 != 0:
        max_page += 1
    if page == 0:
        await call.answer("Вы на первой странице")
        return
    elif page == max_page + 1:
        await call.answer("Вы на последней странице")
        return

    articles = crud.get_articles_by_account_id(account_id, page=page)
    msg_text = "<b>Бот мониторит:\n\n</b>"
    for index, article in enumerate(articles):
        card: schemas.CardOut = await wb_api.get_card(article.id)
        msg_text += f'{num_emoji[index]} {card.name}, Бренд: {card.brand}, Артикул: <u>{article.id}</u>, Мин. цена: ' \
                    f'{article.min_price} ₽\n\n'
    await call.message.edit_text(msg_text, reply_markup=user_kb.get_my_monitoring_articles(account_id, page, max_page))


@dp.callback_query_handler(Text(startswith="find_my_monitoring_article"))
async def find_my_monitoring_article(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split(":")[1])
    await call.message.edit_text("<b>Введите артикул, по которому нужно найти отслеживание</b>",
                                 reply_markup=user_kb.gef_back_to_my_monitoring_articles_menu(account_id))
    await FindMonitoringArticle.article.set()
    await state.update_data(account_id=account_id)
    await state.update_data(have_article=True)


@dp.message_handler(state=FindMonitoringArticle.article)
async def show_my_monitoring_article(message: Message, state: FSMContext):
    try:
        article_id = int(message.text)
    except ValueError:
        await message.answer("Введите целое число!")
        return

    data = await state.get_data()
    account = crud.get_account(data["account_id"])

    if not await wb_api.get_card(article_id):
        await message.answer("Артикул не найден")
        return
    if not await wb_api.is_my_card(account.api_key, article_id):
        await message.answer("Данный артикул не принадлежит этому аккаунту")
        return

    await state.update_data(article_id=article_id)
    article = crud.get_article_by_id_an_account_id(article_id, data["account_id"])
    if not article:
        await message.answer("<b>Отслеживание не найдено</b>\nВведите корректный артикул", reply_markup=user_kb.back_to_menu)
        return
    card = await wb_api.get_card(article_id)
    await message.answer(f"""Артикул: <u>{card.id}</u>
<b>Сейчас</b>
Цена ДО скидки: {card.priceU // 100}р
Размер скидки: {card.sale}%

Цена: <b>{card.salePriceU // 100}р</b>
Мин. цена: {article.min_price}""", reply_markup=user_kb.get_monitoring_article_menu(article_id))


@dp.callback_query_handler(Text(startswith="change_monitoring_article"), state=FindMonitoringArticle.article)
async def change_monitoring_article(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Укажите минимальную цену, ниже которой цена товара не должна опускаться")
    await EditMonitoring.price.set()


@dp.callback_query_handler(Text(startswith="export_excel"))
async def export_excel(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    account = crud.get_account(account_id)
    articles = crud.get_full_articles_by_account_id(account_id)
    excel_api.create_export_data(account, articles)
    await call.message.answer_document(open("docs/" + account.name + ".xlsx", "rb"),
                                       caption="<b>Данные успешно получены</b>",
                                       reply_markup=user_kb.get_edit_account_monitoring(account_id))
    os.remove("docs/" + account.name + ".xlsx")
    await call.answer()
