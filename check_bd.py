from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "#"
engine = create_async_engine(DATABASE_URL, echo=True)


async def test_connection():
    async with engine.begin() as conn:
        await conn.run_sync(lambda connection: print("Connected to database"))


import asyncio

asyncio.run(test_connection())
