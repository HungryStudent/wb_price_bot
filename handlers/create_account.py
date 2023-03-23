from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
import keyboards.user as user_kb
from states.user import CreateAccount
from config import video_1, video_2
from create_bot import dp
from core import crud, schemas
from core.enums import AccountTypes


@dp.callback_query_handler(text="add_account")
async def add_account_info(call: CallbackQuery):
    await call.message.edit_text("""<b>БЕЗОПАСНОЕ ПОДКЛЮЧЕНИЕ ПО API</b>

Ваши данные передаются в <b>зашифрованном</b> виде и надежно хранятся на нашем сервере.

Функционал бота реализован <b>исключительно</b> под работу с ценами.

<b>В любой момент вы можете удалить созданный API ключ</b> в кабинете WB.

🟢 <b>Автоматический</b> - бот автоматически поднимет цену, если она снизится ниже минимальной 

🟡 <b>Полуавтоматический</b> - бот пришлет уведомление и запросит подтверждения на смену цены.



<b>ПОДКЛЮЧЕНИЕ БЕЗ API</b>

🔴 <b>Только уведомление</b> - в этом режиме вы не сможете управлять ценами на WB, но будет доступен режим мониторинга цен (только уведомления)""",
                                 reply_markup=user_kb.add_account)


@dp.callback_query_handler(Text(startswith="start_add_account"))
async def start_add_account(call: CallbackQuery, state: FSMContext):
    account_type = int(call.data.split(":")[1])
    if account_type in [AccountTypes.automate.value, AccountTypes.half_automate.value]:
        await call.message.answer_video(video_1, caption="""<b>Введите API ключ</b>

1️⃣ Перейдите в кабинет продавца WB <b>в Настройки->Доступ к новому API</b>

2️⃣ Введите любое имя ключа, например, <b>price_edit</b> и нажмите “Создать ключ”

3️⃣ Скопируйте появившийся “Ключ для работы с API” и отправьте его нам.""",
                                        reply_markup=user_kb.back_to_add_account_from_video)

    elif account_type == AccountTypes.notify.value:
        await call.message.answer_video(video_2, caption="""1️⃣ Откройте любой ваш товар на WB

2️⃣ Нажмите на название магазина (НЕ НА БРЕНД)

3️⃣ Скопируйте ссылку на страницу и отправьте ее нам. Ссылка будет иметь вид:

https://www.wildberries.ru/seller/1""",
                                        reply_markup=user_kb.back_to_add_account_from_video)
    await call.message.delete()
    await state.set_state(CreateAccount.key)
    await state.update_data(account_type=account_type)


@dp.callback_query_handler(text="back_to_add_account_from_video", state="*")
async def back_to_add_account_from_video(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("""<b>БЕЗОПАСНОЕ ПОДКЛЮЧЕНИЕ ПО API</b>

Ваши данные передаются в <b>зашифрованном</b> виде и надежно хранятся на нашем сервере.

Функционал бота реализован <b>исключительно</b> под работу с ценами.

<b>В любой момент вы можете удалить созданный API ключ</b> в кабинете WB.

🟢 <b>Автоматический</b> - бот автоматически поднимет цену, если она снизится ниже минимальной 

🟡 <b>Полуавтоматический</b> - бот пришлет уведомление и запросит подтверждения на смену цены.



<b>ПОДКЛЮЧЕНИЕ БЕЗ API</b>

🔴 <b>Только уведомление</b> - в этом режиме вы не сможете управлять ценами на WB, но будет доступен режим мониторинга цен (только уведомления)""",
                              reply_markup=user_kb.add_account)
    await call.message.delete()


@dp.message_handler(state=CreateAccount.key)
async def enter_key(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["account_type"] == AccountTypes.notify.value:
        if message.text.startswith(""):
            try:
                await state.update_data(seller_id=int(message.text.replace("https://www.wildberries.ru/seller/", "")))
            except ValueError:
                await message.answer("Введите корректную ссылку")
                return
        else:
            await message.answer("Введите корректную ссылку")
            return
    else:
        await state.update_data(api_key=message.text)
    await message.answer("Введите произвольное название (оно видно только вам)")
    await state.set_state(CreateAccount.name)


@dp.message_handler(state=CreateAccount.name)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()

    account = schemas.AccountCreate(**data, user_id=message.from_user.id)
    res = crud.add_account(account)
    if res == "IntegrityError":
        await message.answer("Аккаунт с таким api ключом или id продавца уже существует",
                             reply_markup=user_kb.back_to_menu)
    else:
        if account.account_type in [AccountTypes.automate.value, AccountTypes.half_automate.value]:
            await message.answer("✅ Готово. Ваш кабинет успешно подключен.", reply_markup=user_kb.back_to_menu)
        elif account.account_type == AccountTypes.notify.value:
            await message.answer("✅ <b>КАБИНЕТ УСПЕШНО ПОДКЛЮЧЕН.</b>", reply_markup=user_kb.back_to_menu)
    await state.finish()