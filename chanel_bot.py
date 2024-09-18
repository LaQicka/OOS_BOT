from telethon import TelegramClient

import config

client = None

async def init():
    global client
    client = TelegramClient('session', config.APP_API, config.APP_HASH)
    await client.connect()

def get_client():
    global client
    return client