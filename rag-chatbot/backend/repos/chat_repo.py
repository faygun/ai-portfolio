import uuid
from typing import List
from asyncpg import Pool
from models.message_info import MessageInfo
from models.session_info import SessionInfo


class ChatRepo:
    def __init__(self, pool: Pool):
        self._pool = pool

    async def create_session(self, user_id, title)-> str:
        session_id = str(uuid.uuid4())
        async with self._pool.acquire() as conn:
            await conn.execute("UPDATE chat_sessions SET ended_at = NOW() WHERE user_id = $1 AND id = (SELECT id FROM chat_sessions ORDER BY started_at DESC LIMIT 1);", user_id)
            row = await conn.execute("INSERT INTO chat_sessions (id, user_id, title) VALUES ($1, $2, $3) ;", session_id, user_id, title)

        return session_id
    
    async def get_system_session(self)-> str:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT id FROM chat_sessions WHERE is_visible = False ORDER BY started_at DESC LIMIT 1;")

            return row.get("id")
        
    async def get_session(self, session_id)-> str:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM chat_sessions WHERE id = $1 LIMIT 1",session_id)

            return row.get("id")
        
    async def get_sessions(self, user_id)-> List[SessionInfo]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, title FROM chat_sessions WHERE user_id = $1 AND is_visible = True ORDER BY started_at DESC", user_id)

            result = []
            for row in rows:
                result.append(SessionInfo(
                    id=str(row.get("id")), 
                    user_id = user_id,
                    title=row.get("title")))

            return result
        
    async def delete_session(self, session_id)-> list[int]:
        async with self._pool.acquire() as conn:
            uploaded_files = await conn.fetch("SELECT id FROM uploaded_files WHERE session_id = $1", session_id)
            row = await conn.execute("DELETE FROM chat_sessions WHERE id = $1 ;", session_id)

            deleted_file_ids = [file["id"] for file in uploaded_files]
            
        return deleted_file_ids

    async def create_message(self, message_info: MessageInfo)-> bool:
        async with self._pool.acquire() as conn:
            row = await conn.execute(
                "INSERT INTO messages (session_id, question, answer, created_at, edited_at) VALUES ($1, $2, $3, $4, $5)",
                message_info.session_id, message_info.question, message_info.answer, message_info.created_at, message_info.edited_at
            )
            
            result = row is not None
            return result

    async def get_messages(self, session_id, limit = 0, isAscending = True):
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM messages WHERE session_id = $1 ORDER BY created_at " + ("ASC" if isAscending else "DESC") + (" LIMIT " + str(limit) if limit > 0 else "" ) + ";", session_id)

            result = []
            for row in rows:
                result.extend([
                    {"role": "human", "content": row.get("question")},
                    {"role": "ai", "content": row.get("answer")}
                ])

            return result