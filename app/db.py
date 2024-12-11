from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# подключение к базе
engine = create_async_engine(url=settings.db.db_url, echo=True, poolclass=NullPool)

# создание подключения к базе
async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=True
)


# получение сессии:
async def get_session():
    async with async_session_maker() as session:
        yield session


# хранение метаданных:
class Base(DeclarativeBase):
    pass