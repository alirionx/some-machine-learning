from time import sleep
import io
import hashlib
import uuid
import ollama
import pdfplumber
from fastapi import File
from minio import Minio
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct, 
    Filter, 
    FieldCondition, 
    MatchValue, 
    FilterSelector,
    ScoredPoint,
    CollectionInfo )


# some config------------------------------
import settings
from models import ChatItem, LlmTask


#------------------------------------------
def get_content_backend_class():
    if settings.CONTENT_BACKEND.lower() == "filesystem": 
        from content_backend_filesystem import ContentBackend 
    elif settings.CONTENT_BACKEND.lower() == "minio": 
        from content_backend_minio import ContentBackend 
    else:
        raise Exception("No valid content backend defined (available => filesystem, minio)")
    return ContentBackend()

#--------------------
def get_memory_backend_class():
    if settings.MEMORY_BACKEND.lower() == "filesystem": 
        from memory_backend_filesystem import MemoryBackend 
    elif settings.MEMORY_BACKEND.lower() == "redis": 
        from memory_backend_redis import MemoryBackend 
    else:
        raise Exception("No valid content backend defined (available => filesystem, redis)")
    return MemoryBackend()

#--------------------
def check_db_prep():
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    if not qdrant.collection_exists(collection_name=settings.DB_COLLECTION):
        qdrant.info()

#--------------------
def list_llm_models()->list[dict]:
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    res = client.list()
    return res.model_dump()['models']

#--------------------
def pull_llm_model(item:LlmTask, stream:bool=False):
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    memory_backend = get_memory_backend_class()
    memory_backend.write_task_memory_by_id(id=item.id, data=item.model_dump())
    if stream:
        progress = client.pull(model=item.model, stream=stream)
        for update in progress:
            if update.completed and update.completed == update.total:
                break
            data = LlmTask(id=item.id, model=item.model, **update.model_dump())
            data.model = item.model 
            memory_backend.write_task_memory_by_id(
                id=item.id, data=data.model_dump())
            sleep(settings.TASK_UPDATE_INTERVAL)
    else:
        progress = client.pull(model=item.model, stream=stream)
        data = LlmTask(id=item.id, model=item.model, **progress.model_dump())
        data.model = item.model
        memory_backend.write_task_memory_by_id(id=item.id, data=data.model_dump())

#--------------------
def delete_llm_model(model:str):
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    client.delete(model=model)

#--------------------
def chat_with_llm(context:list[ChatItem], 
                  model:str=settings.LLMMODEL_DEFAULT_CHAT) -> list[ChatItem]:    
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    message = [ item.model_dump() for item in context ]
    response = client.chat(model=model, messages=message)
    item = ChatItem(**response.message.model_dump())
    item.model = model
    context.append(item)
    return context

#--------------------
def extract_pages_from_pdf(pdf_bytes:bytes) -> list[str]:
    file_like = io.BytesIO(pdf_bytes)
    content = [] 
    with pdfplumber.open(file_like) as pdf:
        for page in pdf.pages:
            content.append(page.extract_text().strip())
    return content

#--------------------
def extract_chunks_from_text(text:str) -> list[str]: 
    if settings.LLMMODEL_CHUNK_SPLITTER in text:
        content = text.split(settings.LLMMODEL_CHUNK_SPLITTER)
    else:
        content = [
            text.strip()[i:i+settings.LLMMODEL_CHUNK_SIZE] for i in range(0, len(text), settings.LLMMODEL_CHUNK_SIZE)
        ]
    return content

#--------------------
def get_embedding(text:str, model:str=settings.LLMMODEL_DEFAULT_EMBED) -> ollama.EmbeddingsResponse:
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    response = client.embeddings(model=model, prompt=text)
    return response

#--------------------
def list_collections() -> list[str]:
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    cols = qdrant.get_collections()
    res = [col.name for col in cols.collections]
    return res

#--------------------
def get_collection(collection_name:str) -> CollectionInfo:
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    res = qdrant.get_collection(collection_name=collection_name)
    return res

#--------------------
def create_collection(collection_name:str, vector_size:int=4096):
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE))

#--------------------
def delete_collection(collection_name:str):
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    if collection_name not in list_collections():
        raise Exception(f"collection '{collection_name}' does not exist.")
    qdrant.delete_collection(collection_name=collection_name)

#--------------------
def clear_collection(collection_name:str):
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    qdrant.delete(
        collection_name=collection_name,
        points_selector=FilterSelector(
            filter=Filter(must=[])
        )
    )

#--------------------
def delete_from_collection_by_hash(text_hash:str):
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    qdrant.delete(
        collection_name=settings.DB_COLLECTION,
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="text_hash",
                        match=MatchValue(value=text_hash)
                    )
                ]
            )
        )
    )

#--------------------
def insert_embeddings_into_collection(
        collection_name:str, 
        doc_name:str, 
        content:list[str], 
        model:str=settings.LLMMODEL_DEFAULT_EMBED) -> str:
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    points = []
    for text in content:
        # UIUIUIUIUIUIUIU
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        text_hash_bytes = hashlib.sha256(text.encode()).digest()
        text_hash_bytes_truncated = text_hash_bytes[:16]
        id = str(uuid.UUID(bytes=text_hash_bytes_truncated))
        
        embedding = get_embedding(text, model=model)
        points.append(PointStruct(
            id=id,
            vector=embedding.embedding,
            payload={
                "text_hash": text_hash, 
                "doc_name": doc_name, 
                "doc_index": content.index(text) + 1,
                "text": text
            }
        ))
    qdrant.upsert(collection_name=collection_name, points=points)

#--------------------
def search_collection(
        collection_name:str, 
        query_text:str, 
        limit:int=5,
        model:str=settings.LLMMODEL_DEFAULT_EMBED) -> list[ScoredPoint]:
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    embedding = get_embedding(text=query_text, model=model)
    hits = qdrant.query_points(
        collection_name=collection_name,
        query=embedding.embedding,
        with_payload=True,
        limit=limit
    )
    return hits.points

#--------------------


#--------------------


#--------------------


#--------------------

