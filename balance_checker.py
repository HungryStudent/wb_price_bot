import asyncio

from core import crud
from create_bot import bot


async def main():
    users = crud.get_users()
    for user in users:
        accounts = crud.get_accounts_with_days_sub(user.user_id)
        for account in accounts:
            if user.balance >= 16:
                user.balance -= 16
                crud.set_account_is_payd(account.id, user.user_id)
            else:
                await bot.send_message(user.user_id, "Баланс на нуле, пополните")
                break
    session = await bot.get_session()
    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
