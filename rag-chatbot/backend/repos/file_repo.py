from datetime import datetime
from typing import List
from contextlib import contextmanager
from models.uploaded_file import UploadedFile
from asyncpg import Pool

class FileRepo:
    def __init__(self, pool:Pool):
        self._pool = pool

    async def insert(self, file:UploadedFile)-> int:
        sql = "INSERT INTO uploaded_files (session_id, name, created_at, edited_at) VALUES ($1, $2, $3, $4) RETURNING *"

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, file.session_id, file.name, file.created_at, file.edited_at)
            
            return row.get("id")
    
    async def delete(self, file_id:int)-> bool:
        sql = "DELETE FROM uploaded_files WHERE id = $1"
        
        async with self._pool.acquire() as conn:
            row = await conn.execute(sql, file_id)
            result = row is not None

            return result
        
    async def getAll(self, session_id:str)-> List[UploadedFile]:
        sql = "SELECT * FROM uploaded_files WHERE session_id = $1"

        result: List[UploadedFile] = []
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, session_id)
            
            for row in rows:
                result.append(
                    UploadedFile(
                        created_at= row.get("created_at"),
                        edited_at= row.get("edited_at"),
                        id= row.get("id"),
                        name= row.get("name"),
                        session_id= str(row.get("session_id"))
                    )
                )
            
            return result

