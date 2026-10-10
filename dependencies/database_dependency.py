from sqlalchemy.ext.asyncio import async_sessionmaker
from database import engine

async_session_local = async_sessionmaker(bind=engine, autoflush=False, autocommit = False)

async def get_db():
    db = async_session_local()
    try:
        yield db
    finally:
        await db.close()