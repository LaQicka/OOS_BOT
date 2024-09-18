from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def generate_admin_menu():
    keyboard = InlineKeyboardBuilder()

    button = InlineKeyboardButton(
        text="Получить отчет по постам за текущую неделю",
        callback_data="week_report"
    )
    keyboard.add(button)

    return keyboard.as_markup()


async def report_menu(cur):
    keyboard = InlineKeyboardBuilder()
    
    button_decrease = InlineKeyboardButton(
        text="-",
        callback_data="week_decrease"
    )
    button_cur = InlineKeyboardButton(
        text=str(cur),
        callback_data="mock"
    )
    button_increase = InlineKeyboardButton(
        text="+",
        callback_data="week_increase"
    )

    keyboard.row(button_decrease, button_cur, button_increase)

    button = InlineKeyboardButton(
        text="Отправить отчет в чат",
        callback_data="week_report_send"
    )
    keyboard.row(button)

    return keyboard.as_markup()