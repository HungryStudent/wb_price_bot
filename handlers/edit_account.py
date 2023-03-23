from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
import keyboards.user as user_kb
from states.user import EditAccount, AddApiKey
from config import video_1
from create_bot import dp
from core import crud, schemas
from core.enums import AccountTypes

monitoring_text = {AccountTypes.automate.value: "Бот сам поднимет цену, если она станет ниже мин. цены",
                   AccountTypes.half_automate.value: "Бот предложит поднять цену, если она станет ниже мин. цены",
                   AccountTypes.notify.value: "Бот пришлет уведомление, если цена станет ниже минимальной."}

monitoring_names = {AccountTypes.automate.value: "Автоматический",
                    AccountTypes.half_automate.value: "Полуавтоматический",
                    AccountTypes.notify.value: "Только уведомление"}


@dp.callback_query_handler(text="show_accounts")
async def show_accounts(call: CallbackQuery):
    accounts = crud.get_accounts(call.from_user.id)
    await call.message.edit_text("Выберите аккаунт, который вы хотите отредактировать",
                                 reply_markup=user_kb.get_accounts(accounts))


@dp.callback_query_handler(Text(startswith="show_account:"))
async def show_account(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    account = crud.get_account(account_id)
    if account.api_key:
        api_key_connected = "🟢 <b>API ключ</b>: Подключен"
    else:
        api_key_connected = "🔴 <b>API ключ</b>: Не подключен"
    await call.message.edit_text(f"""{account.name}
{api_key_connected}
👀 Мониторинг: {monitoring_text[account.account_type]}""", reply_markup=user_kb.get_account(account_id))


@dp.callback_query_handler(Text(startswith="edit_account"))
async def edit_account(call: CallbackQuery, state: FSMContext):
    field = call.data.split(":")[1]
    account_id = int(call.data.split(":")[2])
    if field == "name":
        await call.message.edit_text("Введите произвольное название (оно видно только вам)",
                                     reply_markup=user_kb.cancel_edit)
    elif field == "api_key":
        await call.message.edit_text("Введите новый API ключ",
                                     reply_markup=user_kb.cancel_edit)
    await state.set_state(EditAccount.value)
    await state.update_data(field=field, account_id=account_id)


@dp.message_handler(state=EditAccount.value)
async def enter_value_for_edit(message: Message, state: FSMContext):
    await state.update_data(value=message.text)
    data = await state.get_data()

    crud.edit_account(schemas.AccountEdit(**data))
    await message.answer("✅ <b>ПОДКЛЮЧЕНИЕ УСПЕШНО ОБНОВЛЕНО.</b>", reply_markup=user_kb.back_to_menu)


@dp.callback_query_handler(Text(startswith="start_edit_monitoring"))
async def start_edit_monitoring(call: CallbackQuery):
    account_id = int(call.data.split(":")[1])
    await call.message.edit_text("""🟢 Автоматический - бот автоматически поднимет цену, если она снизится ниже минимальной   

🟡 Полуавтоматический - бот пришлет уведомление и запросит подтверждения на смену цены.    

🔴 Только уведомление - в этом режиме бот будет присылать только уведомления""",
                                 reply_markup=user_kb.get_edit_monitoring(account_id))


@dp.callback_query_handler(Text(startswith="edit_monitoring:"))
async def edit_monitoring(call: CallbackQuery):
    account_type = int(call.data.split(":")[1])
    account_id = int(call.data.split(":")[2])
    if account_type in [AccountTypes.automate.value, AccountTypes.half_automate.value]:
        account = crud.get_account(account_id)
        if account.api_key:
            crud.edit_account(schemas.AccountEdit(account_id=account_id, field="account_type", value=account_type))
            await call.message.edit_text(f"""✅ <b>ПОДКЛЮЧЕНИЕ УСПЕШНО ОБНОВЛЕНО.</b>

Установлен режим мониторинга:  
{monitoring_names[account_type]}""", reply_markup=user_kb.back_to_menu)

        else:
            await call.message.edit_text("""❗ <b>КЛЮЧ НЕ НАЙДЕН.</b> 

Добавить API ключ?""", reply_markup=user_kb.get_add_api_key(account_id, account_type))

    else:
        crud.edit_account(schemas.AccountEdit(account_id=account_id, field="account_type", value=account_type))
        await call.message.edit_text(f"""✅ <b>ПОДКЛЮЧЕНИЕ УСПЕШНО ОБНОВЛЕНО.</b>

Установлен режим мониторинга:  
{monitoring_names[account_type]}""", reply_markup=user_kb.back_to_menu)


@dp.callback_query_handler(Text(startswith="add_api_key"))
async def start_add_api_key(call: CallbackQuery, state: FSMContext):
    account_id = call.data.split(":")[1]
    account_type = call.data.split(":")[2]
    await state.set_state(AddApiKey.api_key)
    await state.update_data(account_id=account_id, account_type=account_type)
    await call.message.answer_video(video_1, caption="""<b>Введите API ключ</b>

1️⃣ Перейдите в кабинет продавца WB <b>в Настройки->Доступ к новому API</b>

2️⃣ Введите любое имя ключа, например, <b>price_edit</b> и нажмите “Создать ключ”

3️⃣ Скопируйте появившийся “Ключ для работы с API” и отправьте его нам.""",
                                    reply_markup=user_kb.back_to_menu_from_video)


@dp.message_handler(state=AddApiKey.api_key)
async def add_api_key(message: Message, state: FSMContext):
    data = await state.get_data()
    crud.edit_account(
        schemas.AccountEdit(account_id=data["account_id"], field="account_type", value=data["account_type"]))
    crud.edit_account(schemas.AccountEdit(account_id=data["account_id"], field="api_key", value=message.text))
    await message.answer("✅ <b>ПОДКЛЮЧЕНИЕ УСПЕШНО ОБНОВЛЕНО.</b>")


@dp.callback_query_handler(Text(startswith="delete_account"))
async def delete_account(call: CallbackQuery):
    account_id = call.data.split(":")[1]
    await call.message.edit_text("""❗ <b>Внимание</b>

Если вы удалите аккаунт, вмести с ним удалятся все активные мониторинги.""",
                                 reply_markup=user_kb.get_delete(account_id))


@dp.callback_query_handler(Text(startswith="sure_delete_account"))
async def sure_delete_account(call: CallbackQuery):
    account_id = call.data.split(":")[1]
    crud.delete_account(account_id)
    await call.message.edit_text("<b>Подключение удалено</b>", reply_markup=user_kb.back_to_menu)