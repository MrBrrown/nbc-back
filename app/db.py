import asyncio
import os
from pathlib import Path
from typing import Generator

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.config import settings, get_alembic_cfg_path, get_project_root
from models.base_model import mapper_registry

db_url = settings.db.db_url
# подключение к базе
engine = create_async_engine(url=db_url, echo=True, poolclass=NullPool)
async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=True)
mapper_registry.configure()

async def init_alembic():
    # Сохраняем текущую рабочую директорию
    current_working_directory = Path.cwd()
    # Путь к файлу alembic.ini
    alembic_cfg_path = get_alembic_cfg_path()
    try:
        os.chdir(get_project_root())
        # Выполнение миграций
        alembic_cfg = AlembicConfig(alembic_cfg_path)
        await asyncio.to_thread(command.upgrade,alembic_cfg, "head")
    except Exception as e:
        print(f"Error applying Alembic migrations: {e}")
    finally:
        # Восстановить текущую рабочую директорию
        os.chdir(current_working_directory)

async def get_session():
    async with async_session_factory() as session:
        yield session

async def get_db() -> Generator[AsyncSession, None, None]:
    async with async_session_factory() as session:
        yield session