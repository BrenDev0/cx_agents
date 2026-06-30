import asyncio

from .core import engine
from .models import Base

async def create_tables():
    print("Creating tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



if __name__ == "__main__":
    asyncio.run(create_tables())