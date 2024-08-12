from sqlalchemy import Column, Integer, String, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    chat_id = Column(Integer, unique=True)
    day_id = Column(Integer)
    start_time=Column(String) 

    def __repr__(self):
        return f"<User(id={self.user_id}, chat_id={self.chat_id}, time={str(self.day_id) + " " + self.start_time})>"
    

async def get_user_by_chat_id(session, chat_id):
    """Получает пользователя по его chat_id.
    Args:
        chat_id: ID чата пользователя.
    Returns:
        Объект User или None, если пользователь не найден.
    """
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(User).where(User.chat_id == chat_id))
            user = result.scalar_one_or_none()
    return user

async def get_all_users(session):
    """Получает список всех пользователей.
    Returns:
        Список объектов User.
    """
    async with session() as s:
        async with s.begin():
            result = await s.execute(select(User))
    return result.scalars().all()

async def create_user(session, user_id, chat_id, day_id, start_time):
    """Создает нового пользователя.
    Args:
        chat_id: ID чата пользователя.
        day_id: ID дня.
        start_time: Время начала.
    Returns:
        Созданный объект User.
    """
    user = User(chat_id=chat_id, user_id=user_id, day_id=day_id, start_time=start_time)
    async with session() as s:
        async with s.begin():
            s.add(user)
    return user

async def delete_user_by_chat_id(session, chat_id):
    """Удаляет пользователя по его chat_id.
    Args:
        chat_id: ID чата пользователя.
    """
    user = await get_user_by_chat_id(session, chat_id)
    async with session() as s:
        async with s.begin():
            if user:
                await s.delete(user)
                await s.commit()

async def update_user(session, user_id, chat_id, day_id, start_time):
    async with session() as s:
        async with s.begin():
            user = await get_user_by_chat_id(session, chat_id)
            if user:
                stmt = update(User).where(User.chat_id == chat_id).values(day_id=day_id, start_time=start_time)
                user.day_id = day_id
                user.start_time = start_time
                await s.execute(stmt)
                await s.commit()

async def create_async_session():
    # engine = create_async_engine('postgresql+asyncpg://user:password@host:port/database')
    engine = create_async_engine(
        'postgresql+asyncpg://'+config.DB_USERNAME+':'+config.DB_PASSWORD+'@'+config.DB_HOST+':'+config.DB_PORT+'/'+config.DB_NAME)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    return async_session