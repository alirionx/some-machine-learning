import sys
from uuid import UUID, uuid4
import mimetypes
import uvicorn

from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Depends, Header, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import settings
from models import StatusMessage, ChatItem, FileItem, Docs2DbList, VectorSearch
import tools



#-Build and prep the App--------------------------------------------
tags_metadata = [
  {
    "name": "api-control",
    "description": "API State and testing",
  },
  {
    "name": "chat",
    "description": "Chat with LLM",
  },
  {
    "name": "content",
    "description": "Data and file management",
  },
  {
    "name": "vector embedding",
    "description": "Vectorization and embedding",
  }
]

app = FastAPI(openapi_tags=tags_metadata)

#-Custom Middleware Functions----------------------------------------
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True
) 

#-The Routes--------------------------------------------------------
@app.get("/", tags=["api-control"], response_model=StatusMessage)
async def api_status_get(request:Request):     
  my_status = StatusMessage(
    message="Hello from the 'SOME-MACHINE-LEARNING' API",
    method=request.method.upper(),
    request_url=request.url._url
  )
  return my_status

#-------------------
@app.get("/chats", tags=["chat"], response_model=list[UUID])
def chats__get():
    try:
        memory_backend = tools.get_memory_backend_class()
        res = memory_backend.list_chat_ids()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return res

#-------------------
@app.get("/chat/newid", tags=["chat"], response_model=UUID)
def chat_newid_get():
    return uuid4()

#-------------------
@app.post("/chat/{id}", tags=["chat"], response_model=list[ChatItem])
def chat_post(id:UUID, item:ChatItem):
    try:
        memory_backend = tools.get_memory_backend_class()
        context = memory_backend.get_chat_memory_by_id(id=id)
        context.append(item)
        context = tools.chat_with_llm(context=context)
        memory_backend.write_chat_memory_by_id(id=id, data=context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return context

#-------------------
@app.get("/chat/{id}", tags=["chat"], response_model=list[ChatItem])
def chat_get(id:UUID):
    try:
        memory_backend = tools.get_memory_backend_class()
        res = memory_backend.get_chat_memory_by_id(id=id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return res

#-------------------
@app.delete("/chat/{id}", tags=["chat"], response_model=UUID)
def chat_delete(id:UUID):
    try:
        memory_backend = tools.get_memory_backend_class()
        memory_backend.delete_chat_memory_by_id(id=id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return id

#-------------------
@app.get("/content", tags=["content"], response_model=list[FileItem])
async def contents_get():
    try:
        content_backend = tools.get_content_backend_class()
        res = content_backend.get_content_list()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return res

#-------------------
@app.post("/content", tags=["content"], response_model=list[FileItem])
def content_post(files: list[UploadFile] = File(...)):
    uploaded_files = []
    content_backend = tools.get_content_backend_class()
    for file in files:
        if mimetypes.guess_type(file.filename)[0] not in settings.CONTENT_ALLOWED_MIMES:
            continue
        try:
            filebytes = file.file.read()
            file_item = content_backend.save_uploaded_content(filename=file.filename, filebytes=filebytes)
            uploaded_files.append(file_item)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to upload {file.filename}: {e}")
    return uploaded_files

#-------------------
@app.get("/content/{filename}", tags=["content"], response_class=StreamingResponse)
def content_get(filename:str):
    content_backend = tools.get_content_backend_class()
    try:
        data = content_backend.get_content_item(filename=filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get {filename}: {e}")
    
    res = StreamingResponse(
        content=data, 
        media_type=mimetypes.guess_type(filename)[0], 
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
    return res

#-------------------
@app.delete("/content/{filename}", tags=["content"], response_model=str)
def content_delete(filename:str):
    content_backend = tools.get_content_backend_class()
    try:
        content_backend.delete_content_item(filename=filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete {filename}: {e}")
    return filename

#-------------------
@app.post("/vector/docs2db", tags=["vector"], response_model=list[FileItem])
def vector_post(item:Docs2DbList, background_tasks: BackgroundTasks):
    processed_items = []
    content_backend = tools.get_content_backend_class()
    file_items = content_backend.get_content_list()
    for fi in [f for f in file_items if f.type in settings.CONTENT_ALLOWED_MIMES and f.type not in item.exclude]:
        bio = content_backend.get_content_item(filename=fi.name)
        chunks = []
        if fi.type == "text/plain":
            chunks = tools.extract_chunks_from_text(text=bio.getvalue().decode("utf-8"))
        elif fi.type == "application/pdf":
            chunks = tools.extract_pages_from_pdf(pdf_bytes=bio.getvalue())
        else:
            continue
        tools.insert_embeddings_into_db(doc_name=fi.name, content=chunks)
        processed_items.append(fi)
    return processed_items

#-------------------
from qdrant_client.models import ScoredPoint
@app.post("/vector/search", tags=["vector"], response_model=list[ScoredPoint])
def vector_post(item:VectorSearch):
    try:
        res = tools.search_vector_db(**item.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search vector db: {e}")
    return res

#-------------------
@app.delete("/vector/clear", tags=["vector"])
def vector_delete():
    try:
        tools.clear_collection()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to clear collection: {e}")

#-------------------




#-------------------




#-The Runner--------------------------------------------------------
if __name__ == "__main__":

    #- App Init---------------------
    try:
        tools.check_db_prep()
    except Exception as e:
        print(f"Fail to init vector DB ({e})")

    #- Start App in desired mode----
    if settings.APP_MODE == "dev" or "dev" in sys.argv:
        print("=> API Mode is: DEV")
        uvicorn.run(app="__main__:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
    else:
        print("=> API Mode is: PROD")
        uvicorn.run(app="__main__:app", host="0.0.0.0", port=settings.API_PORT)

  
#-------------------------------------------------------------------