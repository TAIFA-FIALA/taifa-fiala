import asyncio
import asyncpg
import os

async def test_db_connection():
    db_url = "postgresql://postgres:stocksight1484@100.75.201.24:5432/TAIFA_db"
    try:
        conn = await asyncpg.connect(db_url)
        print("Successfully connected to the database!")
        await conn.close()
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

if __name__ == "__main__":
    asyncio.run(test_db_connection())