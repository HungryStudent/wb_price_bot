import asyncio
import sys

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core import crud, wb_api
from core.enums import AccountTypes, SubTypes
from create_bot import bot


def get_kb_for_change_price(account_id, article_id, price):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Изменить", callback_data=f"price_checker_change:{account_id}:{article_id}:{price}"),
        InlineKeyboardButton("Не изменять", callback_data="price_checker_no_change"))


async def main(sub_type):
    accounts = []
    if sub_type == SubTypes.forever.value:
        accounts = crud.get_accounts_with_payd_forever_sub()
    elif sub_type == SubTypes.days.value:
        accounts = crud.get_accounts_with_payd_days_sub()
    for account in accounts:
        articles = crud.get_full_articles_by_account_id(account.id)
        change_articles = []
        for article in articles:
            card = await wb_api.get_card(article.id)
            if card.salePriceU // 100 < article.min_price:
                change_price = int(article.min_price / (1 - 0.01 * card.sale))
                change_articles.append({"nmId": article.id, "price": change_price, "min_price": article.min_price})
        if change_articles:
            if account.account_type == AccountTypes.automate.value:
                await wb_api.change_price_all(account.api_key, change_articles)
                msg_text = "На следующие артикулы была поднята цена до минимальной:\n"
                for change_article in change_articles:
                    msg_text += f"- {change_article['nmId']}"
                await bot.send_message(account.user_id, msg_text)
            elif account.account_type == AccountTypes.half_automate.value:
                sleep_time = 0
                if len(change_articles) > 5:
                    sleep_time = 0.01
                for change_article in change_articles:
                    await bot.send_message(account.user_id,
                                           f"Цена на артикул {change_article['nmId']} меньше минимальной.",
                                           reply_markup=get_kb_for_change_price(account.id, change_article["nmId"],
                                                                                change_article["price"]))
                    await asyncio.sleep(sleep_time)
            elif account.account_type == AccountTypes.notify.value:
                msg_text = "У этих артикулов цена ниже минимальной:\n"
                for change_article in change_articles:
                    msg_text += f"- {change_article['nmId']}"
                await bot.send_message(account.user_id, msg_text)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[0]))
