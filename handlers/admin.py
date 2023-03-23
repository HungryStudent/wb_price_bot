import asyncio

from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from create_bot import dp
from config import ADMINS
import keyboards.admin as admin_kb
import states.admin as states


@dp.message_handler(content_types="video")
async def send_video_file_id(message: Message):
    await message.answer(message.video.file_id)


@dp.message_handler(lambda m: m.from_user.id in ADMINS, commands="stats")
async def show_stats(message: Message):
    stat = db.get_stat()
    await message.answer(f"Пользователей: {stat['users_count']}\nЗа сегодня: {stat['today_users_count']}")


@dp.message_handler(lambda m: m.from_user.id in ADMINS, commands="send")
async def enter_text(message: Message):
    await message.answer("Введите текст рассылки", reply_markup=admin_kb.cancel)
    await states.Mailing.text.set()


@dp.message_handler(lambda m: m.from_user.id in ADMINS, state=states.Mailing.text)
async def start_send(message: Message, state: FSMContext):
    await message.answer("Начал рассылку")
    await state.finish()
    users = db.get_users()
    count = 0
    block_count = 0
    for user in users:
        try:
            await message.bot.send_message(user["user_id"], message.text)
            count += 1
        except:
            block_count += 1
        await asyncio.sleep(0.1)
    await message.answer(
        f"Количество получивших сообщение: {count}. Пользователей, заблокировавших бота: {block_count}")
