from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from core import schemas
from core.enums import AccountTypes, account_type_text

menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Редактировать цены", callback_data="edit_price"),
    InlineKeyboardButton("Редактировать мониторинг цен", callback_data="monitoring_menu"),
    InlineKeyboardButton("👥 Реферальная программа", callback_data="ref_system"),
    InlineKeyboardButton("💬 Техподдержка", callback_data="support"),
    InlineKeyboardButton("👤 Личный кабинет", callback_data="personal_account"),
    InlineKeyboardButton("⚙ Настройки", callback_data="settings"))

ref_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Зачислить на баланс", callback_data="ref_balance_to_account"),
    InlineKeyboardButton("Вывести на карту", callback_data="withdraw_ref_balance"),
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))

lk_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Пополнить", callback_data="top_up_balance"),
    InlineKeyboardButton("Купить навсегда", callback_data="buy_forever_menu"),
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))

price_change_type = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Цена ДО скидки", callback_data="pre_change_price:pre_price"),
    InlineKeyboardButton("Размер скидки", callback_data="pre_change_price:sale"),
    InlineKeyboardButton("⬅ Назад", callback_data="back_to_enter_price_for_change_article"))

approve_change_price = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("✅ Применить цену на WB", callback_data="approve_change_price"),
    InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu"),
    InlineKeyboardButton("⬅ Назад", callback_data="back_to_price_change_type"))

finish_change_price = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Изменить ещё цену", callback_data="edit_price"),
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))

cancel_edit = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("❌ Отменить", callback_data="settings"))

back_to_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))

back_to_menu_from_pay = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Оплатить", pay=True),
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu_from_video"))

back_to_menu_from_video = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu_from_video"))

back_to_personal_account = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⬅ Назад", callback_data="personal_account"))

back_to_add_account_from_video = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⬅ Назад", callback_data="back_to_add_account_from_video"))

back_to_edit_price = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⬅ Назад", callback_data="edit_price"))

setting_and_menu = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("⚙ Настройки", callback_data="settings"),
                                                         InlineKeyboardButton("⏪ Главное меню",
                                                                              callback_data="back_to_menu"))

settings_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Добавить аккаунт", callback_data="add_account"),
    InlineKeyboardButton("Редактировать", callback_data="show_accounts"),
    InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))

add_account = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🟢 Автоматический", callback_data="start_add_account:1"),
    InlineKeyboardButton("🟡 Полуавтоматический", callback_data="start_add_account:2"),
    InlineKeyboardButton("🔴 Только уведомления", callback_data="start_add_account:3"),
    InlineKeyboardButton("⬅ Назад", callback_data="settings"))

try_again_enter_article = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⬅ Попробовать снова", callback_data="try_again_enter_article"))


def get_accounts(accounts: List[schemas.AccountOut]):
    kb = InlineKeyboardMarkup(row_width=1)
    for account in accounts:
        kb.add(InlineKeyboardButton(account_type_text[account.account_type] + account.name,
                                    callback_data=f"show_account:{account.id}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="settings"),
           InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))
    return kb


def get_account(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("📝 Изменить название", callback_data=f"edit_account:name:{account_id}"),
        InlineKeyboardButton("🔑 API ключ", callback_data=f"edit_account:api_key:{account_id}"),
        InlineKeyboardButton("👀 Режим мониторинга", callback_data=f"start_edit_monitoring:{account_id}"),
        InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_account:{account_id}"),
        InlineKeyboardButton("⬅ Назад", callback_data="show_accounts"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_edit_monitoring(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🟢 Автоматический", callback_data=f"edit_monitoring:1:{account_id}"),
        InlineKeyboardButton("🟡 Полуавтоматический", callback_data=f"edit_monitoring:2:{account_id}"),
        InlineKeyboardButton("🔴 Только уведомления", callback_data=f"edit_monitoring:3:{account_id}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_add_api_key(account_id, account_type):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Добавить", callback_data=f"add_api_key:{account_id}:{account_type}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_delete(account_id):
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("❌ Отменить", callback_data="settings"),
                                                 InlineKeyboardButton("Удалить",
                                                                      callback_data=f"sure_delete_account:{account_id}"))


def get_accounts_for_edit_price(accounts):
    kb = InlineKeyboardMarkup(row_width=1)
    for account in accounts:
        if account.api_key:
            api_key_connected = "🟢 "
        else:
            api_key_connected = "🔴 "
        kb.add(InlineKeyboardButton(api_key_connected + account.name,
                                    callback_data=f"edit_price_by_account:{account.id}"))
    kb.add(InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))
    return kb


def get_accounts_for_monitoring(accounts: List[schemas.AccountOut]):
    kb = InlineKeyboardMarkup(row_width=1)
    for account in accounts:
        kb.add(InlineKeyboardButton(account_type_text[account.account_type] + account.name,
                                    callback_data=f"monitoring_by_account:{account.id}"))
    kb.add(InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))
    return kb


def get_monitoring_menu(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Добавить / изменить", callback_data=f"edit_monitoring_account:{account_id}"),
        InlineKeyboardButton("Массовое редактирование", callback_data=f"mass_edit_account_monitoring:{account_id}"),
        InlineKeyboardButton("Отслеживаемые артикулы", callback_data=f"my_monitoring_articles_menu:{account_id}"),
        InlineKeyboardButton("⬅ Назад", callback_data="monitoring_menu")
    )


def get_edit_account_monitoring(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"monitoring_by_account:{account_id}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_article_for_monitoring(article_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("❌ Отмена", callback_data="monitoring_menu"),
        InlineKeyboardButton("⬅ Назад",
                             callback_data=f"monitoring_by_account:{article_id}"))


def get_finish_change_monitoring_price(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"monitoring_by_account:{account_id}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_my_monitoring_articles_menu(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Список отслеживаний", callback_data=f"my_monitoring_articles:{account_id}:1"),
        InlineKeyboardButton("Поиск по артикулу", callback_data=f"find_my_monitoring_article:{account_id}"),
        InlineKeyboardButton("Выгрузить Excel", callback_data=f"export_excel:{account_id}"),
        InlineKeyboardButton("⬅ Назад", callback_data=f"monitoring_by_account:{account_id}"))


def get_my_monitoring_articles(account_id, page, max_page):
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"my_monitoring_articles_menu:{account_id}")).add(
        InlineKeyboardButton("⬅", callback_data=f"my_monitoring_articles:{account_id}:{page - 1}"),
        InlineKeyboardButton(f"{page}/{max_page}", callback_data="empty"),
        InlineKeyboardButton("➡", callback_data=f"my_monitoring_articles:{account_id}:{page + 1}")
    )


def gef_back_to_my_monitoring_articles_menu(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"my_monitoring_articles_menu:{account_id}"))


def get_monitoring_article_menu(article_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("📝 Изменить", callback_data=f"change_monitoring_article:{article_id}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_mass_edit_account_monitoring(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Выгрузить Excel", callback_data=f"export_excel:{account_id}"),
        InlineKeyboardButton("Загрузить Excel", callback_data=f"import_excel:{account_id}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_back_to_mass_edit_account_monitoring(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"mass_edit_account_monitoring:{account_id}"))


def get_back_to_mass_edit_account_monitoring_with_menu(account_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Редактировать мониторинг цен",
                             callback_data=f"mass_edit_account_monitoring:{account_id}"),
        InlineKeyboardButton("⏪ Главное меню", callback_data="back_to_menu"))


def get_accounts_for_buy_forever(accounts: List[schemas.AccountOut]):
    kb = InlineKeyboardMarkup(row_width=1)
    for account in accounts:
        kb.add(InlineKeyboardButton(account.name, callback_data=f"buy_forever:{account.id}"))
    kb.add(InlineKeyboardButton("⬅ Назад", callback_data="personal_account"))
    return kb
