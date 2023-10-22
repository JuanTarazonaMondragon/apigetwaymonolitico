# -*- coding: utf-8 -*-
"""Database session configuration."""
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

SQLALCHEMY_DATABASE_URL = os.getenv(
    'SQLALCHEMY_DATABASE_URL',
    "sqlite+aiosqlite:///./payments.db"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    future=True
)

Base = declarative_base()
