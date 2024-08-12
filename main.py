import asyncio
import logging
import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient
from telethon.tl.types import PeerChannel

import config, db
import handlers
from handlers import router

client = TelegramClient('session', config.APP_API, config.APP_HASH)

bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

def get_start_of_current_week():
    today = datetime.date.today()
    # Получаем день недели (0 - понедельник, 6 - воскресенье)
    weekday = today.weekday()
    days_to_monday = weekday % 7
    monday = today - datetime.timedelta(days=days_to_monday)
    return monday

async def get_channel_history():
    """Получает историю сообщений канала за последнюю неделю"""
    messages = []
    required_date = get_start_of_current_week()
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
        print(user)
        print(is_event_passed_this_week(user.day_id, user.start_time))
        if is_event_passed_this_week(user.day_id, user.start_time):
            posted = any(message['sender_id'] == user.user_id for message in messages)
            print(posted)
            if posted == False:
                await bot.send_message(user.chat_id, text="Во избежании экзекуции вам следует сделать пост в ООС")


async def main():
    await client.connect()
    session = await db.create_async_session()
    handlers.session = session
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_for_notifications, 'interval', minutes=60)
    scheduler.start()

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())