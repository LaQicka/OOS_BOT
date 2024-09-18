import datetime
from telethon.tl.types import PeerChannel

import config

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


def is_event_passed_this_week(weekday, time_str):
    """Проверяет, прошло ли событие на этой неделе."""
    now = datetime.datetime.now()
    event_day = now - datetime.timedelta(days=now.weekday() - weekday)
    event_datetime = datetime.datetime.combine(event_day, datetime.datetime.strptime(time_str, "%H:%M").time())

    return event_datetime <= now


async def get_channel_history(client):
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


async def get_chat_users(client):
    partic = client.iter_participants(PeerChannel(channel_id=config.TOPIC_ID))
    partic_map = {}
    async for p in partic:
        if p.username != None and p.username != "TheHeraldOfWill_bot":
            partic_map.update({p.id: p.username})
    return partic_map


async def get_users_post_status(week_offset, client):
    partic = await get_chat_users(client)
    who_post = {}
    who_didnt_post = {}
    start, end = get_week_range(week_offset)
    async for message in client.iter_messages(PeerChannel(channel_id=config.TOPIC_ID)
                                              ,reply_to=1
                                              ,limit=100):
        if message.date.date() >= start and message.date.date() <= end:
            if message.from_id.user_id in partic:
                who_post.update({message.from_id.user_id: partic[message.from_id.user_id]})
    
    for user_id in partic:
        if user_id not in who_post:
            who_didnt_post[user_id] = partic[user_id]
    return who_post, who_didnt_post


async def generate_users_post_report(week_offset, client):
    start, end = get_week_range(week_offset)
    who_post, who_didnt_post = await get_users_post_status(week_offset, client)
    text = "Отчет по неделе " + str(start) + " - " + str(end) + "\n"
    text += "\nГерои, почтившие устои и сделавшие пост\n"
    for user_id in who_post:
        string = "✅ " + str(who_post[user_id]) + "\n"
        text += string
    
    text += "\nРенегады, уклонивщиеся от службы в этот раз\n"
    for user_id in who_didnt_post:
        string = "❌ " + str(who_didnt_post[user_id]) + "\n"
        text += string
    
    return text