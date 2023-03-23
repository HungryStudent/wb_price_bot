from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions, ChatMember

import keyboards.admin as admin_kb
import keyboards.user as user_kb
from states import user as states
from config import ADMINS, SUPPORT_NAME
from create_bot import dp
from core import crud, schemas

from datetime import datetime


@dp.message_handler(commands=['start'], state="*")
async def start_command(message: Message, state: FSMContext):
    await state.finish()

    inviter_id = message.get_args()

    if inviter_id in ["", str(message.from_user.id)]:
        inviter_id = 0

    crud.add_user(
        schemas.UserCreate(user_id=message.from_user.id, username=message.from_user.username, reg_time=datetime.now(),
                           inviter_id=inviter_id))

    await message.answer("HEllo", reply_markup=user_kb.menu)


@dp.callback_query_handler(text="back_to_menu", state="*")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("HEllo", reply_markup=user_kb.menu)


@dp.callback_query_handler(text="back_to_menu_from_video", state="*")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("HEllo", reply_markup=user_kb.menu)
    await call.message.delete()


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод отменен", reply_markup=user_kb.menu)


@dp.callback_query_handler(text="support")
async def show_support(call: CallbackQuery):
    await call.message.edit_text(f"""По всем вопросам и предложениям вы можете связаться с нами тут: @{SUPPORT_NAME}""",
                                 reply_markup=user_kb.back_to_menu)


@dp.callback_query_handler(text="settings", state="*")
async def show_settings(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("""<b>Настройки</b>
Добавьте или отредактируйте подключенные аккаунты WB.

Вы можете подключить любое кол-во аккаунтов.""", reply_markup=user_kb.settings_menu)


@dp.callback_query_handler(text="personal_account")
async def personal_account(call: CallbackQuery):
    user = crud.get_user(call.from_user.id)
    await call.message.edit_text(f"""<b>Профиль</b>

Ваш баланс: <b>{user.balance} руб.</b>
Подключено ЛК по подписке: {user.days_count}
Подключено ЛК навсегда: {user.forever_count}


<b>Тариф "ПО ДНЯМ"</b>
+ Цены обновляются каждые <b>10 минут</b>
1 личный кабинет: <b>16₽ / день</b>
Подключено может быть любое количество аккаунтов


<b>Тариф "НАВСЕГДА"</b>
+ Цены обновляются каждые 5 минут
1 аккаунт - 9900₽
Каждый последующий - 4900₽""", reply_markup=user_kb.lk_menu)
