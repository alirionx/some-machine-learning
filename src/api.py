import sys
from uuid import UUID, uuid4
import mimetypes
import uvicorn

from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Depends, Header, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from qdrant_client.models import ScoredPoint, CollectionInfo

import settings
from models import (
    LlmPullList,
    LlmTask,
    StatusMessage, 
    ChatItem, 
    FileItem, 
    Doc2Collection, 
    VectorSearch, 
    VectorCollection
)
import tools



#-Build and prep the App--------------------------------------------
tags_metadata = [
  {
    "name": "api-control",
    "description": "API State and testing",
  },
  {
    "name": "llm",
    "description": "LLM binary management",
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
    "name": "vector",
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

#------------------------------------------------------
@app.get("/llms", tags=["llm"], response_model=list[dict])
def llm_get():
    try:
        res = tools.list_llm_models()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return res

#-------------------
@app.post("/llm/pull", tags=["llm"], response_model=list[LlmTask])
def llm_pull_post(items:LlmPullList, background_tasks: BackgroundTasks):
    res = []
    for model in items.models:
        res.append(
            LlmTask(model=model, id=uuid4())
        )
        background_tasks.add_task(tools.pull_llm_model, model)
    return res

#-------------------
@app.delete("/llm", tags=["llm"], response_model=str)
def llm_get(model:str):
    try:
        tools.delete_llm_model(model=model)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return model

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

#------------------------------------------------------
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

#------------------------------------------------------
@app.get("/vector/collections", tags=["vector"], response_model=list[str])
def vector_collections_get():
    try:
        res = tools.list_collections()
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    return res

#-------------------
@app.get("/vector/collection/{collection_name}", tags=["vector"], response_model=CollectionInfo)
def vector_collection_get(collection_name:str):
    try:
        res = tools.get_collection(collection_name=collection_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"collection '{e}' not found")
    return res

#-------------------
@app.post("/vector/collection", tags=["vector"], response_model=CollectionInfo)
def vector_collection_post(item:VectorCollection):
    try:
        tools.create_collection(
            collection_name=item.collection_name, vector_size=item.vector_size)
        res = tools.get_collection(collection_name=item.collection_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"collection '{e}' not found")
    return res

#-------------------
@app.delete("/vector/clear/{collection_name}", tags=["vector"])
def vector_clear_delete(collection_name):
    try:
        tools.clear_collection(collection_name=collection_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to clear collection: {e}")

#-------------------
@app.delete("/vector/collection/{collection_name}", tags=["vector"], response_model=str)
def vector_collection_delete(collection_name:str):
    try:
        tools.delete_collection(collection_name=collection_name)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"collection '{e}' not found")
    return collection_name

#-------------------
@app.post("/vector/doc2collection", tags=["vector"], response_model=FileItem)
def vector_doc2collection_post(item:Doc2Collection, background_tasks: BackgroundTasks):
    content_backend = tools.get_content_backend_class()
    if item.collection_name not in tools.list_collections():
        raise HTTPException(404, f"collection '{item.collection_name}' does not exist.")
    if item.doc_name not in [ fi.name for fi in content_backend.get_content_list()]:
        raise HTTPException(404, f"content '{item.doc_name}' does not exist.")
    try:
        fi = content_backend.get_content_item(filename=item.doc_name)
        bio = content_backend.get_content_bio(filename=item.doc_name)
        chunks = []
        if fi.type == "text/plain":
            chunks = tools.extract_chunks_from_text(text=bio.getvalue().decode("utf-8"))
        elif fi.type == "application/pdf":
            chunks = tools.extract_pages_from_pdf(pdf_bytes=bio.getvalue())
        else:
            raise HTTPException(400, "invalid file type")
        tools.insert_embeddings_into_collection(
            collection_name=item.collection_name, 
            doc_name=item.doc_name,
            content=chunks)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)
    return fi

#-------------------
@app.post("/vector/search", tags=["vector"], response_model=list[ScoredPoint])
def vector_post(item:VectorSearch):
    try:
        res = tools.search_collection(**item.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search vector db: {e}")
    return res

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