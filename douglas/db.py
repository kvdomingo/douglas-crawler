from collections.abc import Callable
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
    contextmanager,
)

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from douglas.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=not settings.IN_PRODUCTION,
    future=True,
)

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=not settings.IN_PRODUCTION,
    future=True,
)

session_maker = sessionmaker(
    engine,
    autoflush=True,
    autocommit=False,
    expire_on_commit=False,
)

async_session_maker = async_sessionmaker(
    async_engine,
    autoflush=True,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    session = session_maker()
    try:
        yield session
    except DatabaseError as e:
        logger.error(f"{e}")
        raise
    finally:
        session.close()


async def aget_db():
    session = async_session_maker()
    try:
        yield session
    except DatabaseError as e:
        logger.error(f"{e}")
        raise
    finally:
        await session.close()


get_db_context: Callable[[], AbstractContextManager[Session]] = contextmanager(get_db)

aget_db_context: Callable[[], AbstractAsyncContextManager[AsyncSession]] = (
    asynccontextmanager(aget_db)
)
