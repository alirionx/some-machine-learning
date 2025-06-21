import os
import hashlib
import uuid
import ollama
import pdfplumber

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
DBHOST = os.environ.get("DBHOST", "localhost")
DBPORT = int((os.environ.get("DBPORT", "6333")))
DBCOLLECTION = os.environ.get("DBCOLLECTION", "ollama_collection")

LLMMODEL_CHAT = os.environ.get("LLMMODEL_CHAT", "mistral")
LLMMODEL_EMBED = os.environ.get("LLMMODEL_EMBED", "avr/sfr-embedding-mistral")

#------------------------------------------
def check_db_prep():
    qdrant = QdrantClient(host=DBHOST, port=DBPORT)
    if not qdrant.collection_exists(collection_name=DBCOLLECTION):
        qdrant.create_collection(
            collection_name=DBCOLLECTION,
            vectors_config=VectorParams(
                size=4096,
                distance=Distance.COSINE
            )
        )

#--------------------
def extract_pages_from_pdf(pdf_path:str) -> list[str]:
    content = [] 
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            content.append(page.extract_text().strip())
    return content

#--------------------
def get_embedding(text:str) -> ollama.EmbeddingsResponse:
    response = ollama.embeddings(model=LLMMODEL_EMBED, prompt=text)
    return response

#--------------------
def insert_embedding_into_db(doc_name:str, content:list[str]) -> str:
    qdrant = QdrantClient(host=DBHOST, port=DBPORT)
    points = []
    for text in content:
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        embedding = get_embedding(text)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.embedding,
            payload={
                "text_hash": text_hash, 
                "doc_name": doc_name, 
                "doc_index": content.index(text) + 1,
                "text": text
            }
        ))
    qdrant.upsert(collection_name=DBCOLLECTION, points=points)

#--------------------
def delete_from_db_by_hash(text_hash:str):
    qdrant = QdrantClient(host=DBHOST, port=DBPORT)
    qdrant.delete(
        collection_name=DBCOLLECTION,
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
def search_vector_db(query_text:str, limit:int=5) -> list[ScoredPoint]:
    qdrant = QdrantClient(host=DBHOST, port=DBPORT)
    embedding = get_embedding(query_text)
    hits = qdrant.query_points(
        collection_name=DBCOLLECTION,
        query=embedding.embedding,
        with_payload=True,
        limit=limit
    )
    return hits.points

#--------------------

