from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

days_dict = {
    'Понедельник': 0,
    'Вторник': 1,
    'Среда': 2,
    'Четверг': 3,
    'Пятница': 4,
    'Суббота': 5,
    'Воскресенье': 6
}


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/start"), KeyboardButton(text="/create_notify")]
], resize_keyboard=True)

async def generate_weekdays_menu():
    keyboard = InlineKeyboardBuilder()  # Создаем клавиатуру с 2 кнопками в ряду

    for day, day_number in days_dict.items():
        button = InlineKeyboardButton(text=day, callback_data="setday_" + str(day_number))
        keyboard.add(button)

    return keyboard.adjust(2).as_markup()


async def generate_hours_menu():
    keyboard = InlineKeyboardBuilder()

    for hour in range(24):
        start_time = f"{hour:02d}:00"
        end_time = f"{hour+1:02d}:00"
        button = InlineKeyboardButton(
            text=f"{start_time}-{end_time}",
            callback_data="sethour_"+start_time
        )
        keyboard.add(button)

    return keyboard.adjust(4).as_markup()


async def approve_kb():
    keyboard = InlineKeyboardBuilder()
    button_approve = InlineKeyboardButton(
        text="Подтвердить",
        callback_data="approve"
    )
    button_deny = InlineKeyboardButton(
        text="Отмена",
        callback_data="deny"
    )
    keyboard.add(button_approve)
    keyboard.add(button_deny)
    return keyboard.as_markup()