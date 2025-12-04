import os
import asyncpg

DATABASE_URL = os.getenv("PG_DB_CONNECTION")

_pool = asyncpg.Pool = None


async def get_pool() -> asyncpg.Pool:
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60,
        )
    return _pool