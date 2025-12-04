from asyncpg import Pool

class UserRepo:
    def __init__(self, pool:Pool):
        self._pool = pool

    async def get_admin_userid(self)-> str:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE email = 'admin@admin.com' LIMIT 1")

            return row.get("id")
