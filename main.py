import aiogram.types
import asyncio
import logging
import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlalchemy
from telethon import TelegramClient
from telethon.tl.types import PeerChannel

import config, db
import handlers
from handlers import router
from handlers_bank.admin_handlers import admin_router
from db import User
import chanel_bot

client = None

bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

# DEPRECATED - delete in next commit
# 
# def get_start_of_current_week():
#     today = datetime.date.today()
#     # Получаем день недели (0 - понедельник, 6 - воскресенье)
#     weekday = today.weekday()
#     days_to_monday = weekday % 7
#     monday = today - datetime.timedelta(days=days_to_monday)
#     return monday


def get_week_range(week_offset=0):
    """
    Вычисляет дату начала и конца недели с учетом смещения.
    Args:
        week_offset: Смещение относительно текущей недели (по умолчанию 0).
            Положительное значение - будущие недели, отрицательное - прошлые.
    Returns:
        Кортеж из двух дат: начала и конца недели.
    """

    today = datetime.date.today()
    # Получаем день недели (0 - понедельник, 6 - воскресенье)
    weekday = today.weekday()
    days_to_monday = weekday % 7

    # Вычисляем дату понедельника текущей недели
    monday = today - datetime.timedelta(days=days_to_monday)

    # Добавляем смещение в днях
    start_date = monday + datetime.timedelta(days=week_offset * 7)
    end_date = start_date + datetime.timedelta(days=6)

    return start_date, end_date


async def get_channel_history():
    """Получает историю сообщений канала за последнюю неделю"""
    messages = []
    required_date, mock = get_week_range(0)
    async for message in client.iter_messages(PeerChannel(channel_id=config.TOPIC_ID)
                                              ,reply_to=1
                                              ,limit=30
                                              ):
        
        if message.date.date() >= required_date:
            messages.append(message)
    return messages


def is_event_passed_this_week(weekday, time_str):
    """Проверяет, прошло ли событие на этой неделе."""
    now = datetime.datetime.now()
    event_day = now - datetime.timedelta(days=now.weekday() - weekday)
    event_datetime = datetime.datetime.combine(event_day, datetime.datetime.strptime(time_str, "%H:%M").time())

    return event_datetime <= now


async def check_for_notifications():
    messages = await get_channel_history()
    users = await db.get_all_users(handlers.session)
    for user in users:
        # print(user)
        # print(is_event_passed_this_week(user.day_id, user.start_time))
        if is_event_passed_this_week(user.day_id, user.start_time):
            posted = any(message.from_id == user.user_id for message in messages)
            if posted == False:
                await bot.send_message(user.chat_id, text="Во избежании экзекуции вам следует сделать пост в ООС")


async def get_chat_users():
    partic = client.iter_participants(PeerChannel(channel_id=config.TOPIC_ID))
    partic_map = {}
    async for p in partic:
        if p.username != None and p.username != "TheHeraldOfWill_bot":
            partic_map.update({p.id: p.username})
    return partic_map


async def get_users_post_status(week_offset):
    partic = await get_chat_users()
    who_post = {}
    who_didnt_post = {}
    start, end = get_week_range(week_offset)
    async for message in client.iter_messages(PeerChannel(channel_id=config.TOPIC_ID)
                                              ,reply_to=1
                                              ,limit=100):
        if message.date.date() >= start and message.date.date() <= end:
            who_post.update({message.from_id.user_id: partic[message.from_id.user_id]})
    
    for user_id in partic:
        if user_id not in who_post:
            who_didnt_post[user_id] = partic[user_id]
    return who_post, who_didnt_post
    

async def generate_users_post_report(week_offset):
    start, end = get_week_range(week_offset)
    who_post, who_didnt_post = await get_users_post_status(week_offset)
    text = "Отчет по неделе " + str(start) + " - " + str(end) + "\n"
    text += "\nГерои, почтившие устои и сделавшие пост\n"
    for user_id in who_post:
        string = "\t✅ " + str(who_post[user_id]) + "\n"
        text += string
    
    text += "\nРенегады, уклонивщиеся от службы в этот раз\n"
    for user_id in who_didnt_post:
        string = "\t❌ " + str(who_didnt_post[user_id]) + "\n"
        text += string
    
    return text


async def send_p():
    text = await generate_users_post_report()
    await bot.send_message(config.ADMIN_ID, text=text)


async def main():
    await chanel_bot.init()
    global client
    client = chanel_bot.get_client()
    

    session = await db.create_async_session()
    handlers.session = session
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_for_notifications, 'interval', minutes=1)
    scheduler.start()

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(router, admin_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())