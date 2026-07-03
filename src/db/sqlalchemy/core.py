from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.settings import settings


engine = create_async_engine(
    url=settings.DATABASE_URL
)

db_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

# Celery tasks run each invocation inside its own asyncio.run() call, which
# creates and tears down a fresh event loop every time. asyncpg connections
# are bound to the loop that opened them, so a pooled connection handed out
# under a later loop breaks with "another operation is in progress". NullPool
# opens a brand-new physical connection per checkout so nothing crosses loops.
worker_engine = create_async_engine(
    url=settings.DATABASE_URL,
    poolclass=NullPool
)

worker_session_maker = async_sessionmaker(bind=worker_engine, expire_on_commit=False)