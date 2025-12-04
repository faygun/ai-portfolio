
import os
from pathlib import Path
from dotenv import load_dotenv

env_path  = ""
ROOT = Path(__file__).resolve().parent

if Path("/.dockerenv").exists():
    env_path = ROOT/".env"
else:
    env_path = ROOT/".env.local"

load_dotenv(dotenv_path=env_path, override=False)

from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from typing import Annotated, Optional
from fastapi.middleware.cors import CORSMiddleware
from helpers.vector_helper import index_document_to_vectordb, remove_document_from_vector_db
from helpers.langchain_helper import get_rag_chain, generate_title
from repos.chat_repo import ChatRepo
from repos.file_repo import FileRepo
from repos.user_repo import UserRepo
from repos.db import get_pool
from models.message_info import MessageInfo
from models.uploaded_file import UploadedFile
from datetime import datetime
import logging
import shutil
from uuid import UUID

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await get_pool()
    print("pool is created...")

    yield

    await app.state.pool.close()
    print("pool is closed...")

app = FastAPI(lifespan=lifespan)

origins = os.getenv("ALLOW_CORS_ORIGINS").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/chat")
async def chat(question: Annotated[str, Form()], user_id: Annotated[str, Form()], session_id: Annotated[Optional[str], Form()] = None, file: Annotated[Optional[UploadFile], File()] = None ):
    # it is temporaryly provided userid, it will be resolved once authentication flow implemented...
    # user_id = "d65013fa-6aae-4f96-a15a-056646927c92"
    
    logging.info(f"Session ID: {session_id}, User Query: {question}")

    chat_repo = ChatRepo(app.state.pool)
    title = ""
    if session_id is None or session_id == "":
        title = generate_title(question)
        session_id = await chat_repo.create_session(user_id, title)
    
    if file != None:
        result = await uploadDoc(file, session_id)
        print(result)
        if result["code"] != 200:
            raise HTTPException(status_code=500, detail="An error occurred while the request processing.", session_id=session_id)

    # old messages will be summarized then included...
    message_history_limit = int(os.getenv("MESSAGE_HISTORY_LIMIT"))
    message_history = await chat_repo.get_messages(session_id, limit = message_history_limit)
    
    rag_chain = get_rag_chain()
    
    answer = rag_chain.invoke({
        "input": question,
        "chat_history": message_history
    })['answer']

    # llm  answer...
    await chat_repo.create_message(MessageInfo(
        session_id=session_id,
        user_id=user_id,
        question=question,
        answer=answer,
        created_at=datetime.now()
    ))

    logging.info(f"Chat session created with ID: {session_id}")
    return {"session_id": session_id, "answer": answer, "title": title}

from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
@app.post("/api/upload-doc")
async def uploadDocument(file: UploadFile = File(...), session_id:str  | None = None):
    # if the session_id is empty, it means the files are uploaded via an API not user interface, therefore we fetch the default session_id that created initially.
    if session_id == "" or session_id == None:
        c_repo = ChatRepo(app.state.pool)
        session_id = await c_repo.get_system_session()

    result = await uploadDoc(file, str(session_id))
    if result["code"] == 400:
        raise HTTPException(status_code=400, detail=result["error"]) 
    elif result["code"] == 500:
        raise HTTPException(status_code=500, detail=result["error"])
    elif result["code"] == 200:
        print(result)
        return JSONResponse(content={"message": result["message"], "file_id": result["file_id"], "result": True})
    else:
        raise HTTPException(status_code=500, detail="An error occurred while the request processing.")

async def uploadDoc(file:UploadedFile, session_id:str) -> dict:
    allowedExtension = [".pdf", ".doc", ".csv", ".html", ".json", ".txt", ".docx"]
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()
    result = {}
    if extension not in allowedExtension:
        result = {"success":False, "error": f"Unsupported file type: {extension}. Supported files are {','.join(allowedExtension)}", "code":400}

        return result

    temp_file_name = f"temp_{file.filename}"

    try:
        with open(temp_file_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # insert filename in database as reference...
        file_repo = FileRepo(app.state.pool)
        file_id = await file_repo.insert(file=UploadedFile(
            name= file.filename,
            session_id=session_id
        ))

        # index document to vector database....
        response = index_document_to_vectordb(temp_file_name, file_id)

        if response:
            result = {"success":True, "code":200, "message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}

        else:
            # delete file record from db...
            await file_repo.delete(file_id)

            result = {"success": False, "error":f"Failed to index {file.filename}.", "code":500}

        return result
    
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)

@app.get("/api/users/admin_user_id")
async def getAdminUserID():
    repo = UserRepo(app.state.pool)
    result = await repo.get_admin_userid()
    return result

@app.get("/api/sessions/{user_id}")
async def listSessions(user_id:str):
    repo = ChatRepo(app.state.pool)
    result = await repo.get_sessions(user_id)
    return result

@app.get("/api/messages/{session_id}")
async def getMessages(session_id:str):
    repo = ChatRepo(app.state.pool)
    result = await repo.get_messages(session_id)
    return result

@app.get("/api/list-docs/{session_id}")
async def listDocs(session_id:str):
    repo = ChatRepo(app.state.pool)

    result = await repo.get_session()

    return result

@app.delete("/api/session/{id}")
async def deleteSession(id:str):
    repo = ChatRepo(app.state.pool)
    try:
        deleted_file_ids = await repo.delete_session(id)

        if(len(deleted_file_ids)):
            for file_id in deleted_file_ids:
                remove_document_from_vector_db(file_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while the request processing. Exception: {e}")
        
    return True

@app.delete("/api/delete-doc/{doc_id}")
async def deleteDoc(file_id:int):
    result = False
    if file_id == 0:
        raise HTTPException(status_code=400, detail=f"DocumentId should be greater than zero.")
    
    result = remove_document_from_vector_db(file_id)
    if result == True:
        repo = FileRepo(app.state.pool)
        result = await repo.delete(file_id)

    return {"result": result}


