from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.settings import settings


engine = create_async_engine(
    url=settings.DATABASE_URL
)

db_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)