from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.DB_URL, connect_args={"check_same_thread" : False})

async_session_local = async_sessionmaker(autoflush=False, autocommit = False, bind = engine)

class Base(DeclarativeBase):
    pass