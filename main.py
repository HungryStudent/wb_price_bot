from aiogram.utils import executor

from core.database import engine
from create_bot import dp

from core import models


async def on_startup(_):
    models.Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


