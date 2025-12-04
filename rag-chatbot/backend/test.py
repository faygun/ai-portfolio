# from helpers.vector_helper import vector_store
# from repos.db import get_pool
# from repos.chat_repo import ChatRepo
# import asyncio
# result = vector_store.get(
#     # where={"file_id": 3},
#     where_document={"$contains": "faruk"},
# )

# print(result)

# results = vector_store._collection.get()
# vector_store.delete_collection()
##print("IDs:", results["ids"])
# print("Documents:", results["documents"])
# print("Metadata:", results["metadatas"])


# docs = vector_store.get(
#         where={"file_id":10}
#         )

# print(f"{len(docs['ids'])} doc chunks found for file_id {10}")

# async def demo():
#     pool = await get_pool()

#     repo = ChatRepo(pool)

#     result = await repo.get_messages("90cce0b4-2388-4a1c-b34a-249b7fb04bdb")

#     print(result)


# asyncio.run(demo())
import os
from dotenv import load_dotenv

load_dotenv()
print(f"allow origin: {os.getenv('ALLOW_CORS_ORIGINS')}")