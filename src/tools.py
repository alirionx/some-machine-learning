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
    QueryResponse )


# some config------------------------------
import settings
from models import ChatItem


#------------------------------------------
def chat_with_llm(context:list[ChatItem]) -> list[ChatItem]:
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    message = [ item.model_dump() for item in context ]
    response = client.chat(model=settings.LLMMODEL_CHAT, messages=message)
    context.append(
        ChatItem(**response.message.model_dump())
    )
    return context

#--------------------
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
        qdrant.create_collection(
            collection_name=settings.DB_COLLECTION,
            vectors_config=VectorParams(
                size=4096,
                distance=Distance.COSINE
            )
        )

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
def get_embedding(text:str) -> ollama.EmbeddingsResponse:
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    response = client.embeddings(model=settings.LLMMODEL_EMBED, prompt=text)
    return response

#--------------------
def insert_embeddings_into_db(doc_name:str, content:list[str]) -> str:
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    points = []
    for text in content:
        # UIUIUIUIUIUIUIU
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        text_hash_bytes = hashlib.sha256(text.encode()).digest()
        text_hash_bytes_truncated = text_hash_bytes[:16]
        id = str(uuid.UUID(bytes=text_hash_bytes_truncated))
        
        embedding = get_embedding(text)
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
    qdrant.upsert(collection_name=settings.DB_COLLECTION, points=points)

#--------------------
def search_vector_db(query_text:str, limit:int=5) -> list[ScoredPoint]:
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    embedding = get_embedding(query_text)
    hits = qdrant.query_points(
        collection_name=settings.DB_COLLECTION,
        query=embedding.embedding,
        with_payload=True,
        limit=limit
    )
    return hits.points

#--------------------
def delete_from_db_by_hash(text_hash:str):
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
def clear_collection():
    qdrant = QdrantClient(host=settings.DB_HOST, port=settings.DB_PORT)
    qdrant.delete(
        collection_name=settings.DB_COLLECTION,
        points_selector=FilterSelector(
            filter=Filter(must=[])
        )
    )

#--------------------


#--------------------


#--------------------


#--------------------

