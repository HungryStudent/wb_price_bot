from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions, ChatMember

import keyboards.admin as admin_kb
import keyboards.user as user_kb
from states.user import ExcelEditMonitoring
from config import ADMINS, video_1, video_2
from create_bot import dp
from core import crud, schemas, wb_api, excel_api
from core.enums import AccountTypes
import os


@dp.callback_query_handler(Text(startswith="mass_edit_account_monitoring"))
async def mass_edit_account_monitoring_menu(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    await call.message.edit_text("<b>Для того, чтобы массово отредактировать мониторинг, вы можете выгрузить шаблон с "
                                 "текущими данными, отредактировать его и отправить обратно в бота.</b>",
                                 reply_markup=user_kb.get_mass_edit_account_monitoring(account_id))


@dp.callback_query_handler(Text(startswith="import_excel"))
async def import_excel(call: CallbackQuery, state: FSMContext):
    account_id = int(call.data.split(":")[1])
    await call.message.edit_text("Пришлите EXCEL файл в чат",
                                 reply_markup=user_kb.get_back_to_mass_edit_account_monitoring(account_id))
    await state.set_state(ExcelEditMonitoring.file)
    await state.update_data(account_id=account_id)


@dp.message_handler(state=ExcelEditMonitoring.file, content_types="document")
async def change_articles_by_excel(message: Message, state: FSMContext):
    data = await state.get_data()
    account_id = data["account_id"]

    filename, file_extension = os.path.splitext(message.document.file_name)
    if file_extension != ".xlsx":
        await message.answer("Неверный формат.\nПришлите EXCEL файл",
                             reply_markup=user_kb.get_back_to_mass_edit_account_monitoring(account_id))
        return

    await message.document.download("docs/" + message.document.file_name)
    articles = excel_api.parse_data("docs/" + message.document.file_name)
    account = crud.get_account(account_id)
    cards = await wb_api.get_my_cards(account.api_key)
    cards = [card["nmId"] for card in cards]
    my_articles = []
    for article in articles:
        if article.id in cards:
            my_articles.append(article)
    crud.changes_articles_by_account_id(account_id, my_articles)
    await message.answer(f"""✅ <b>УСПЕШНО УСТАНОВЛЕНО</b>

Обновлено: {len(my_articles)} арт. """,
                         reply_markup=user_kb.get_back_to_mass_edit_account_monitoring_with_menu(account_id))
    await state.finish()
