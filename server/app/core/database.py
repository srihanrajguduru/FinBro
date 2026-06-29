# --------------------------------------------------------
# File: server/app/core/database.py
# Purpose: Database Connection Engine & Session Configuration
# Responsibilities: Configures SQLAlchemy asynchronous engine and sessionmaker,
#                   defines the Declarative Base, and exposes the get_db session generator.
# Author: Srihan Raj Guduru
# --------------------------------------------------------

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """
    Common base class for all SQLAlchemy model definitions.
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session and commits/rolls back automatically.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
